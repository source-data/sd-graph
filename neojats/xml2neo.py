from lxml.etree import parse, XMLParser
import re
from typing import List
from zipfile import ZipFile, BadZipFile
from pathlib import Path
from io import BytesIO
from argparse import ArgumentParser
from neo4j.exceptions import ClientError
from .model import JATS_GRAPH_MODEL
from neotools.xml2neo import build_neo_graph, XMLNode
from .queries import (
    SOURCE_BY_UUID, 
    CREATE_FULLTEXT_INDEX_ON_ABSTRACT,
    CREATE_FULLTEXT_INDEX_ON_CAPTION,
    CREATE_FULLTEXT_INDEX_ON_NAME,
    CREATE_FULLTEXT_INDEX_ON_TITLE,
)
from . import logger, DB


DEBUG_MODE = False


class ArchiveLoader:

    def __init__(self, path: Path, glob_pattern='*.meca', check_for_duplicate=False):
        self.path = path
        self.archives = self.path.glob(glob_pattern)
        self.check_for_duplicate = check_for_duplicate
        self.parser = XMLParser(load_dtd=True, no_network=True, recover=True)

    def load_full_text(self, z: ZipFile, meca_archive, path_full_text: str):
        with z.open(path_full_text) as full_text_xml:
            print(f"parsing {meca_archive}/{path_full_text}")
            xml = parse(full_text_xml, parser=self.parser).getroot() # root is <article>
            source = meca_archive.name
            xml_node = XMLNode(xml, JATS_GRAPH_MODEL)
            build_neo_graph(xml_node, source, DB)

    def already_loaded(self, meca_archive: Path):
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            found_one = results.single() is not None
            summary = results.summary()
            notifications = summary.notifications
            if notifications:
                print(f"WARNING: {notifications} when checking for duplicates.")
                print(summary.statement)
                print(summary.parameters)
            return found_one
        query = SOURCE_BY_UUID
        query.params = {'source': meca_archive.name}
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
        for count, meca_archive in enumerate(self.archives):
            if self.check_for_duplicate and self.already_loaded(meca_archive):
                print(f"WARNING: {meca_archive.name} already loaded. Skipping.", end="\r")
                skipped += 1 
            else:
                try:
                    with ZipFile(meca_archive) as z:
                        xml_file_list = [f for f in z.namelist() if Path(f).suffix == '.xml']
                        path_full_text = self.extract_from_manifest(z)
                        if path_full_text not in xml_file_list:
                            msg = f"WARNING: the file {path_full_text} indicated in the manifest is not in {meca_archive}"
                            print(msg)
                            logger.warning(msg)
                            path_full_text = self.find_alternative(xml_file_list, path_full_text)
                            print(f"Trying {path_full_text} instead.")
                        self.load_full_text(z, meca_archive, path_full_text)
                except BadZipFile:
                    logger.error(f"not a zip file: {meca_archive}")
        print()
        print(f"skipped {skipped} out of {count+1}")


def add_indices():
    try:
        DB.query(CREATE_FULLTEXT_INDEX_ON_ABSTRACT)
        DB.query(CREATE_FULLTEXT_INDEX_ON_CAPTION)
        DB.query(CREATE_FULLTEXT_INDEX_ON_NAME)
        DB.query(CREATE_FULLTEXT_INDEX_ON_TITLE)
    except ClientError as error:
        print()
        print(error)


def self_test():
    xml_str = b'''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.2d1 20170631//EN" "JATS-archivearticle1.dtd">
    <article xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" article-type="article" dtd-version="1.2d1" specific-use="production" xml:lang="en">
        <front>
            <article-meta>
                <article-id pub-id-type="doi">10.1101/2020.03.02.972935</article-id>
                <article-version>1.1</article-version>
                <title-group>
                    <article-title>Isolation 'and' "characterization"  $of {SARS-CoV-2} from H&#x00F4;pital Bichat the first \US COVID-19 patient</article-title>
                </title-group>
                <abstract>This is the abstract.</abstract>              
                <contrib-group>
                    <contrib contrib-type="author">
                        <contrib-id contrib-id-type="orcid">http://orcid.org/0000-0002-1012-2226</contrib-id>
                        <name><surname>Liu</surname><given-names>Chuang</given-names></name>
                        <xref ref-type="aff" rid="a1">1</xref>
                        <xref ref-type="aff" rid="a3">3</xref>
                        <xref ref-type="author-notes" rid="n2">&#x002A;</xref>
                    </contrib>
                    <contrib contrib-type="author">
                        <name><surname>Yang</surname><given-names>Yang</given-names></name>
                        <xref ref-type="aff" rid="a2">2</xref>
                        <xref ref-type="author-notes" rid="n2">&#x002A;</xref>
                    </contrib>
                </contrib-group>
                <pub-date pub-type="epub"><year>2020</year></pub-date>
            </article-meta>
        </front>
        <body>
            THis and that.
            <fig>
                <label>Figure 3</label>
                <caption>This is nice.</caption>
                <graphic xlink:href="http://this.com/figure/3"/>
            </fig>
        </body>
    </article>
    '''
    tree = parse(BytesIO(xml_str))
    xml_element = tree.getroot()
    graph = XMLNode(xml_element, JATS_GRAPH_MODEL)
    print(graph)
    build_neo_graph(graph, 'test')


if __name__ == '__main__':
    parser = ArgumentParser(description='Parsing xml documents from meca archive and loading into neo4j.')
    parser.add_argument('path', nargs="?", help='Paths to directory containing meca archives.')
    parser.add_argument('--no_duplicate_check', action="store_true", help="Use flag to remove check on whether a paper has already been loaded.")
    args = parser.parse_args()
    path = args.path
    check_for_duplicate = not args.no_duplicate_check
    if path:
        ArchiveLoader(Path(path), check_for_duplicate=check_for_duplicate).load_dir()
        add_indices()
    else:
        self_test()
