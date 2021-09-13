from lxml.etree import parse, XMLParser
from argparse import ArgumentParser
from pathlib import Path
from io import BytesIO
from typing import Dict
import common.logging
from neotools.txt2node import XMLNode
from neotools.rxiv2neo import build_neo_graph
from neo4j.exceptions import ConstraintError
from .model import (
    CHEBI_GRAPH_MODEL,
    GO_GRAPH_MODEL,
    UNIPROT_GRAPH_MODEL,
    CVCL_GRAPH_MODEL,
    CL_GRAPH_MODEL,
    UBERON_GRAPH_MODEL,
    NCBITAXON_GRAPH_MODEL,
    DOID_GRAPH_MODEL,
    OBI_GRAPH_MODEL,
    BAO_GRAPH_MODEL,
)
from .queries import MAKE, REMOVE_DEPRECATED, CONTRAINT_CLASS_UNIQUE
from . import DB


def load_ontology(path: Path, graph_model: Dict):
    with open(path) as file:
        print(f"parsing {path}")
        parser = XMLParser(remove_blank_text=True)
        xml = parse(file, parser=parser).getroot()
        namespaces = xml.nsmap
        if None in namespaces:
            namespaces['default'] = namespaces[None]  # XPath does not have None as namespace entry; so creating one if needed
            del namespaces[None]  # need to remove it otherwise XPath raises TypeError: empty namespace prefix is not supported in XPath
        # compile(graph_model, namespaces)
        source = path.name
        print()
        xml_node = XMLNode(xml, graph_model, namespaces=namespaces)
        print()
        DB.query(CONTRAINT_CLASS_UNIQUE()) # some ontologies share classes, will raise neobolt.exceptions.ConstraintError
        build_neo_graph(xml_node, source, DB, ConstraintError)
        print()
        res = DB.query(REMOVE_DEPRECATED())
        for row in res:
            print("REMOVE_DEPRECATED: ", "; ".join([str(row[column]) for column in REMOVE_DEPRECATED.returns]))
        res = DB.query(MAKE())
        for row in res:
            print("MAKE: ", "; ".join([str(row[column]) for column in MAKE.returns]))


# map of local file names with graph model
ALL_GRAPH_MODELS = {
    'go.owl': GO_GRAPH_MODEL,
    'uniprot_sprot.xml': UNIPROT_GRAPH_MODEL,
    'uniprot-test.owl': UNIPROT_GRAPH_MODEL,
    'uberon.owl': UBERON_GRAPH_MODEL,
    'chebi.owl': CHEBI_GRAPH_MODEL,
    'cellosaurus.xml': CVCL_GRAPH_MODEL,
    'cl.owl': CL_GRAPH_MODEL,
    'ncbitaxon.owl': NCBITAXON_GRAPH_MODEL,
    'doid.owl': DOID_GRAPH_MODEL,
    'obi.owl': OBI_GRAPH_MODEL,
    'bao.xrdf': BAO_GRAPH_MODEL
}


def self_test():
    xml_str = b'''<?xml version="1.0"?>
<rdf:RDF xmlns="http://purl.obolibrary.org/obo/doid.owl#"
    xml:base="http://purl.obolibrary.org/obo/doid.owl"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:obo="http://purl.obolibrary.org/obo/"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:xml="http://www.w3.org/XML/1998/namespace"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:doid="http://purl.obolibrary.org/obo/doid#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:terms="http://purl.org/dc/terms/"
    xmlns:oboInOwl="http://www.geneontology.org/formats/oboInOwl#">
    <owl:Ontology rdf:about="http://purl.obolibrary.org/obo/doid.owl">
        <owl:versionIRI rdf:resource="http://purl.obolibrary.org/obo/doid/releases/2020-04-20/doid.owl"/>
        <owl:imports rdf:resource="http://purl.obolibrary.org/obo/doid/obo/ext.owl"/>
        <dc:description rdf:datatype="http://www.w3.org/2001/XMLSchema#string">The Disease Ontology has been developed as a standardized ontology for human disease with the purpose of providing the biomedical community with consistent, reusable and sustainable descriptions of human disease terms, phenotype characteristics and related medical vocabulary disease concepts.</dc:description>
        <dc:title rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Human Disease Ontology</dc:title>
        <terms:license rdf:resource="https://creativecommons.org/publicdomain/zero/1.0/"/>
        <oboInOwl:date rdf:datatype="http://www.w3.org/2001/XMLSchema#string">20:04:2020 16:19</oboInOwl:date>
        <oboInOwl:default-namespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">disease_ontology</oboInOwl:default-namespace>
        <oboInOwl:hasOBOFormatVersion rdf:datatype="http://www.w3.org/2001/XMLSchema#string">1.2</oboInOwl:hasOBOFormatVersion>
        <oboInOwl:saved-by rdf:datatype="http://www.w3.org/2001/XMLSchema#string">lschriml</oboInOwl:saved-by>
        <rdfs:comment rdf:datatype="http://www.w3.org/2001/XMLSchema#string">The Disease Ontology content is available via the Creative Commons Public Domain Dedication CC0 1.0 Universal license (https://creativecommons.org/publicdomain/zero/1.0/).</rdfs:comment>
    </owl:Ontology>
    <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_0001816">
        <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/DOID_175"/>
        <obo:IAO_0000115 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">A vascular cancer that derives_from the cells that line the walls of blood vessels or lymphatic vessels.</obo:IAO_0000115>
        <oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">disease_ontology</oboInOwl:hasOBONamespace>
        <oboInOwl:id rdf:datatype="http://www.w3.org/2001/XMLSchema#string">DOID:0001816</oboInOwl:id>
        <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">angiosarcoma</rdfs:label>
    </owl:Class>
    <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_265">
        <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/DOID_0001816"/>
        <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/DOID_672"/>
        <rdfs:subClassOf>
            <owl:Restriction>
                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0001025"/>
                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/UBERON_0002106"/>
            </owl:Restriction>
        </rdfs:subClassOf>
        <obo:IAO_0000115 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">An angiosarcoma and hemangioma of intra-abdominal structure and malignant soft tissue neoplasm of the spleen that results_in a nonhematolymphoid malignant neoplasm of the spleen.</obo:IAO_0000115>
        <oboInOwl:hasExactSynonym xml:lang="en">Splenic hemangiosarcoma</oboInOwl:hasExactSynonym>
        <oboInOwl:hasExactSynonym xml:lang="en">angiosarcoma of spleen</oboInOwl:hasExactSynonym>
        <oboInOwl:id rdf:datatype="http://www.w3.org/2001/XMLSchema#string">DOID:265</oboInOwl:id>
        <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">spleen angiosarcoma</rdfs:label>
    </owl:Class>
</rdf:RDF>
'''
    parser = XMLParser(remove_blank_text=True)
    tree = parse(BytesIO(xml_str), parser=parser)
    xml_element = tree.getroot()
    namespaces = xml_element.nsmap
    del namespaces[None]
    graph = XMLNode(xml_element, DOID_GRAPH_MODEL, namespaces=namespaces)
    print(graph)
    res = DB.query(CONTRAINT_CLASS_UNIQUE())
    build_neo_graph(graph, 'test', DB)
    print()
    res = DB.query(REMOVE_DEPRECATED())
    res = DB.query(MAKE())
    for row in res:
        print("; ".join([str(row[column]) for column in MAKE.returns]))


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading the disease ontology into neo4j.')
    parser.add_argument('path', nargs="?", help='Paths to owl file.')
    args = parser.parse_args()
    path = args.path
    if path:
        path = Path(path)
        graph_model = ALL_GRAPH_MODELS[path.name]
        load_ontology(path, graph_model)
        # add_indices()
    else:
        self_test()
