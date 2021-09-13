from lxml.etree import parse, XMLParser
import re
import pandas as pd
import json
from typing import List
from zipfile import ZipFile, BadZipFile
from pathlib import Path
from argparse import ArgumentParser
from neo4j.exceptions import ClientError
import common.logging
from .model import JATS_GRAPH_MODEL, CORD19_GRAPH_MODEL
from .txt2node import XMLNode, JSONNode
from .db import Instance
from .queries import (
    SOURCE_BY_UUID,
    CREATE_INDEX_DOI,
    CREATE_INDEX_VERSION,
)
from . import DB

logger = common.logging.get_logger(__name__)


DEBUG_MODE = False


class MECALoader:

    def __init__(self, path: Path, glob_pattern='*.meca', check_for_duplicate=False):
        self.path = path
        self.archives = self.path.glob(glob_pattern)
        self.check_for_duplicate = check_for_duplicate
        self.parser = XMLParser(load_dtd=True, no_network=True, recover=True)

    def load_full_text(self, z: ZipFile, meca_archive, path_full_text: str):
        with z.open(path_full_text) as full_text_xml:
            logger.info(f"parsing {meca_archive}/{path_full_text}")
            xml = parse(full_text_xml, parser=self.parser).getroot() # root is <article>
            source = meca_archive.name
            xml_node = XMLNode(xml, JATS_GRAPH_MODEL)
            build_neo_graph(xml_node, source, DB)

    def already_loaded(self, meca_archive: Path):
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            found_one = results.single() is not None
            summary = results.consume()
            notifications = summary.notifications
            if notifications:
                logger.warning(f"WARNING: {notifications} when checking for duplicates.")
                logger.warning(summary.statement)
                logger.warning(summary.parameters)
            return found_one
        query = SOURCE_BY_UUID(params={'source': meca_archive.name})
        found_it = DB.query_with_tx_funct(tx_funct, query)
        return found_it

    def extract_from_manifest(self, z: ZipFile):
        with z.open('manifest.xml') as manifest:
            x_manifest = parse(manifest).getroot()
            ns = {'ns': x_manifest.nsmap[None]}
            article_item = x_manifest.xpath('ns:item[@type="article"]/ns:instance[@media-type="application/xml"]', namespaces=ns)[0]
            path_full_text = article_item.attrib['href']
        return path_full_text

    def find_alternative(self, xml_file_list: List, path_full_text):
        for filename in xml_file_list:
            basename_from_manifest = Path(path_full_text).stem
            existing_basename = Path(filename).stem
            # trying conservative method to find an alternative xml file with only version number as alteration
            if re.match(basename_from_manifest + r'v\d+', existing_basename):
                break
        return filename

    def load_dir(self):
        skipped = 0
        count = 0
        for count, meca_archive in enumerate(self.archives):
            if self.check_for_duplicate and self.already_loaded(meca_archive):
                logger.warning(f"WARNING: {meca_archive.name} already loaded. Skipping.", end="\r")
                skipped += 1
            else:
                try:
                    with ZipFile(meca_archive) as z:
                        xml_file_list = [f for f in z.namelist() if Path(f).suffix == '.xml']
                        path_full_text = self.extract_from_manifest(z)
                        if path_full_text not in xml_file_list:
                            msg = f"WARNING: the file {path_full_text} indicated in the manifest is not in {meca_archive}"
                            logger.warning(msg)
                            path_full_text = self.find_alternative(xml_file_list, path_full_text)
                            logger.warning(f"Trying {path_full_text} instead.")
                        self.load_full_text(z, meca_archive, path_full_text)
                except BadZipFile:
                    logger.error(f"not a zip file: {meca_archive}")
        logger.info()
        if count is not None:
            logger.info(f"skipped {skipped} out of {count+1}")
        else:
            logger.info(f"No archives found!")


class CORDLoader:

    def __init__(self, path: Path, journals: List, check_for_duplicate=False):
        self.path = path
        self.journals = journals
        self.metadata = self.get_metadata(self.path / 'metadata.csv')
        self.check_for_duplicate = check_for_duplicate

    def get_metadata(self, path: Path):
        metadata = None
        with open(path) as metadata_file:
            r = pd.read_csv(metadata_file)
            metadata = r.loc[(r['source_x'].isin(self.journals)) & (r['pdf_json_files'].notna()), ['doi', 'publish_time', 'pdf_json_files', 'source_x']]
        return metadata

    def load_full_text(self, json_path: Path, supplementary_metadata):
        full_path = self.path / json_path
        with open(full_path) as json_archive:
            logger.info(f"parsing {json_archive.name}")
            j = json.load(json_archive)
            # unfortunately CORD-19 documents are not self-contained
            # part of the metadata needs to be reinserted a posteriori
            j['metadata']['doi'] = supplementary_metadata['doi']
            j['metadata']['pub_date'] = supplementary_metadata['publish_time']
            j['metadata']['journal-title'] = supplementary_metadata['source_x']
            json_node = JSONNode(j, CORD19_GRAPH_MODEL)
            logger.info(json_node)
            source = json_archive.name
            build_neo_graph(json_node, source, DB)

    def already_loaded(self, archive: Path):
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            found_one = results.single() is not None
            summary = results.consume()
            notifications = summary.notifications
            if notifications:
                logger.warning(f"WARNING: {notifications} when checking for duplicates.")
                logger.warning(summary.statement)
                logger.warning(summary.parameters)
            return found_one
        query = SOURCE_BY_UUID
        query.params = {'source': archive.name}
        found_it = DB.query_with_tx_funct(tx_funct, query)
        return found_it

    def load_dir(self):
        skipped = 0
        count = None
        for count, archive_metadata in self.metadata.iterrows():
            json_path = Path(archive_metadata['pdf_json_files'])
            if self.check_for_duplicate and self.already_loaded(json_path):
                logger.warning(f"WARNING: {json_path.name} already loaded. Skipping.", end="\r")
                skipped += 1
            else:
                self.load_full_text(json_path, archive_metadata)
        logger.info()
        if count is not None:
            logger.info(f"skipped {skipped} out of {count+1}")
        else:
            logger.info(f"No archives found!")


class NoException(Exception):
    """
    A default Exception that is never caught
    """
    def __init__(self):
        super().__init__()


def build_neo_graph(py_node, source: str, db: Instance, catch_exception: Exception = NoException):
    properties = py_node.properties  # deal with types!
    properties['source'] = source
    try:
        node = db.node(py_node)
    except catch_exception as e:
        logger.error(e)
        logger.error(f"Exception with {py_node.label}")
        node = None
    except NoException as e:
        raise e
    if node is not None:
        logger.info(f"loaded {py_node.label} as node {node.id}                                ", end="\r")
        for rel, children in py_node.children.items():
            for child in children:
                child_node = build_neo_graph(child, source, db, catch_exception)
                if rel is not None:
                    db.relationship(node, child_node, rel)
    return node


def add_indices():
    try:
        DB.query(CREATE_INDEX_DOI())
        DB.query(CREATE_INDEX_VERSION())
    except ClientError as error:
        logger.error()
        logger.error(error)


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('path', nargs="?", help='Paths to directory containing the archives.')
    parser.add_argument('-Y', '--type', choices=['meca','cord19'], help="Type or archive.")
    parser.add_argument('--no_duplicate_check', action="store_true", help="Use flag to remove check on whether a paper has already been loaded.")
    args = parser.parse_args()
    path = args.path
    type = args.type
    check_for_duplicate = not args.no_duplicate_check

    if path:
        if type == 'meca':
            MECALoader(Path(path), check_for_duplicate=check_for_duplicate).load_dir()
        else:  # type == 'cord19':
            CORDLoader(Path(path), ['MedRxiv']).load_dir()
        add_indices()
    else:
        logger.info("no path, nothing to do!")
