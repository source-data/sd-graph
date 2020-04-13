from lxml.etree import Element, XMLParser, parse
from typing import Dict
import re
from zipfile import ZipFile
from pathlib import Path
from io import BytesIO
from argparse import ArgumentParser
from .utils import inner_text
from neotools.db import Cypher
from . import DB

NS = {
    'w': 'http://www.wiley.com/namespaces/wiley',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}

DEBUG_MODE = False


GRAPH_MODEL = {
    'has_doi': {
        'XPath': 'front/article-meta/article-id[@pub-id-type="doi"]',
        'children': {}
    },
    'has_title': {
        'XPath': 'front/article-meta/title-group/article-title',
        'children': {}
    },
    'has_figure': {
        'XPath': './/fig',
        'children': {
            'has_label': {'XPath': 'label', 'children': {}},
            'has_caption': {'XPath': 'caption', 'children': {}},
            'has_graphic': {'XPath': 'graphic', 'children': {}},
        }
    },
}


def quote4neo(attributes):
    quotes_added = {}
    for k, v in attributes.items():
        if isinstance(v, str):
            v = '"' + v.replace("'", r"\'").replace('"', r'\"') + '"'
        quotes_added[k] = v
    return quotes_added


def cleanup_name(name):
    hyphen = re.compile(r'-')
    ns_prefix = re.compile(r'^{\S+}')
    name = hyphen.sub('_', name)
    name = ns_prefix.sub('', name)
    return name


def cleanup_properties(properties):
    clean_prop = {cleanup_name(k): v for k, v in properties.items()}
    return clean_prop


class XMLNode:
    """
    Nodes formed by recursively traversing the xml tree using the graph model.
    The properties of the nodes are copied from the attributes of the xml element.
    If there are no children to be found, it is a terminal node and the innertext is used as text property.
    The graph model determines wich subset of children elements that have to be extracted.
    For each subset of children, the graph model provides an XPath to find them.

    Args:
        element (Element): the xml element to use to creat the node
        children (Dict): the subgraph model that tells which children to find with which XPath

    Attributes:
        label: the node label
        properties: the properties of the node
        children (Dict): the nodes' list of childrens

    """
    def __init__(self, element: Element, graph_model: Dict):
        self.label = cleanup_name(element.tag).capitalize()
        properties = element.attrib or {}
        if graph_model:
            properties['text'] = element.text or ''
        else:
            properties['text'] = inner_text(element)
        properties['tail'] = element.tail or ''
        self.properties = cleanup_properties(properties)
        self.children = self.find_children(element, graph_model)

    def find_children(self, element, graph_model):
        graph = {}
        for relationship in graph_model:
            xp = graph_model[relationship]['XPath']
            sub_model = graph_model[relationship]['children']
            elements = element.xpath(xp)
            sub_graph = [XMLNode(e, sub_model) for e in elements]
            graph[relationship] = sub_graph
        return graph

    def to_str(self, indent=0):
        indentation = "    " * indent
        s = ""
        s += indentation + f"({self.label} {self.properties})\n"
        for rel in self.children:
            s += indentation + f"-[{rel}]->\n"
            for c in self.children[rel]:
                s += indentation + c.to_str(indent+1) + "\n"
        return s

    def __str__(self):
        return self.to_str()


def build_neo_graph(xml_node: XMLNode, source: str):
    properties = xml_node.properties
    properties['source'] = source
    node = DB.node(xml_node)

    for rel, children in xml_node.children.items():
        for child in children:
            child_node = build_neo_graph(child, source)
            DB.relationship(node, child_node, rel)
    return node


def load_dir(path: Path):
    for meca_archive in path.glob('*.meca'):
        with ZipFile(meca_archive) as z:
            with z.open('manifest.xml') as manifest:
                x_manifest = parse(manifest).getroot()
                ns = {'ns': x_manifest.nsmap[None]}
                article_item = x_manifest.xpath('ns:item[@type="article"]/ns:instance[@media-type="application/xml"]', namespaces=ns)[0]
                path_full_text = article_item.attrib['href']
            with z.open(path_full_text) as full_text_xml:
                print(f"parsing {path_full_text}")
                xml = parse(full_text_xml).getroot()
                source = meca_archive.name
                xml_node = XMLNode(xml, GRAPH_MODEL)
                print(f"graph from {xml_node.children['has_doi'][0].properties['text']}")
                build_neo_graph(xml_node, source)


def self_test():
    xml_str = b'''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Archiving and Interchange DTD v1.2d1 20170631//EN" "JATS-archivearticle1.dtd">
    <article xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" article-type="article" dtd-version="1.2d1" specific-use="production" xml:lang="en">
        <front>
            <article-meta>
                <article-id pub-id-type="doi">10.1101/2020.03.02.972935</article-id>
                <title-group>
                    <article-title>Isolation and characterization of SARS-CoV-2 from the first US COVID-19 patient</article-title>
                </title-group>
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
    graph = XMLNode(xml_element, GRAPH_MODEL)
    print(graph)
    build_neo_graph(graph, 'test')


if __name__ == '__main__':
    parser = ArgumentParser(description='Generative Adverserial Trainer for fraud detection.')
    parser.add_argument('path', help='Paths to directory contraining meca archives.')
    args = parser.parse_args()
    path = args.path
    path = Path(path)
    if path:
        load_dir(path)
    else:
        self_test()
