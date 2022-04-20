from lxml.etree import parse
from io import BytesIO
from unittest import TestCase
from .model import JATS_GRAPH_MODEL, CORD19_GRAPH_MODEL, CROSSREF_PREPRINT_API_GRAPH_MODEL
from .txt2node import XMLNode, JSONNode, ParsingError


class TestJSONNode(JSONNode):
    def __init__(self, label: str, properties: dict, children: dict = {}):
        self.label = label
        self.properties = properties
        self.children = children


class NodeTestCase(TestCase):

    def assert_nodes_equal(self, expected: JSONNode, actual: JSONNode):
        self.assertEqual(expected.label, actual.label)
        self.assertDictEqual(expected.properties, actual.properties)
        self.assertSetEqual(set(expected.children.keys()), set(actual.children.keys()))
        for relationship in expected.children.keys():
            expecteds_relationships = expected.children[relationship]
            actuals_relationships = actual.children[relationship]
            self.assertEqual(len(expecteds_relationships), len(actuals_relationships))
            for i in range(len(expecteds_relationships)):
                sub_node_expected = expecteds_relationships[i]
                sub_node_actual = actuals_relationships[i]
                self.assert_nodes_equal(sub_node_expected, sub_node_actual)


class JSONNodeTestCase(NodeTestCase):

    def test_cord(self):
        input = {
            "paper_id": "0b159ec402f822d502c0a2a478f5e08c1212acb5",
            "metadata": {
                "title": "Cloning and characterization of a putative mouse acetyl-CoA transporter cDNA",
                "doi": "sdlkfjsdlkfjsf",
                "pub_date": "2020-05-30",
                "authors": [
                    {
                        "first": "Roop",
                        "middle": [],
                        "last": "Singh Bora",
                        "email": ""
                    },
                    {
                        "first": "Akiko",
                        "middle": [],
                        "last": "Kanamori",
                        "suffix": "",
                        "affiliation": {
                            "laboratory": "Laboratory for Cellular Glycobiology",
                            "institution": "The Institute of Physical and Chemical Research",
                            "location": {
                                "addrLine": "2-1 Hirosawa",
                                "postCode": "351-0198",
                                "settlement": "Wako",
                                "region": "Saitama",
                                "country": "Japan"
                            }
                        },
                        "email": ""
                    },
                ],
            },
            "abstract": [
                {
                    "text": "blah blah blah",
                    "section": "Abstract"
                },
                {
                    "text": "following up: blah.",
                    "section": "abstract"
                }
            ],
            "ref_entries": {
                "FIGREF0": {
                    "text": "Nucleotide sequence and predicted amino-acid sequence of brane domain III. This motif is often found in the mouse Acatn cDNA. The potential N-linked glycosylation sites are enclosed in the boxes. The putative leucine zipper motif is underlined. transporter proteins(Eckhardt et al., 1996;Abeijon The nucleotide sequence data will appear in the DDBJ/EMBL/ et al., 1996).GenBank nucleotide sequence databases with the accession number Homology searches of mouse Acatn against currently AB016795.",
                    "latex": None,
                    "type": "figure"
                },
                "FIGREF1": {
                    "text": "Immunocytochemical analysis to study the expression of O-acetylated gangliosides in the transfected cells. HeLa/GT3+ cells were transfected with vector pcDNA3.1 (A) or pcDNA3.1-Acatn (B). Bar=20 mm.",
                    "latex": None,
                    "type": "figure"
                },
            }
        }
        expected_node = TestJSONNode(
            label='Article',
            properties={'doi': 'sdlkfjsdlkfjsf', 'pub_date': '2020-05-30', 'title': 'Cloning and characterization of a putative mouse acetyl-CoA transporter cDNA', 'abstract': 'blah blah blah following up: blah.', 'position_idx': 0},
            children={
                'has_author': [
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Roop', 'surname': 'Singh Bora', 'position_idx': 0},
                    ),
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Akiko', 'surname': 'Kanamori', 'position_idx': 1},
                    ),
                ],
                'has_figure': [
                    TestJSONNode(
                        label='Fig',
                        properties={'label': 'FIGREF0', 'caption': 'Nucleotide sequence and predicted amino-acid sequence of brane domain III. This motif is often found in the mouse Acatn cDNA. The potential N-linked glycosylation sites are enclosed in the boxes. The putative leucine zipper motif is underlined. transporter proteins(Eckhardt et al., 1996;Abeijon The nucleotide sequence data will appear in the DDBJ/EMBL/ et al., 1996).GenBank nucleotide sequence databases with the accession number Homology searches of mouse Acatn against currently AB016795.', 'position_idx': 0},
                    ),
                    TestJSONNode(
                        label='Fig',
                        properties={'label': 'FIGREF1', 'caption': 'Immunocytochemical analysis to study the expression of O-acetylated gangliosides in the transfected cells. HeLa/GT3+ cells were transfected with vector pcDNA3.1 (A) or pcDNA3.1-Acatn (B). Bar=20 mm.', 'position_idx': 1},
                    ),
                ],
            }
        )
        actual_node = JSONNode(input, CORD19_GRAPH_MODEL)
        self.assert_nodes_equal(expected_node, actual_node)

    def test_crossref(self):
        input = {
            "institution": [
                {
                    "name": "bioRxiv",
                    "place": ["-"],
                    "acronym": ["-"]
                }
            ],
            "indexed": {
                "date-parts": [[2020, 5, 9]], 
                "date-time": "2020-05-09T05:10:49Z",
                "timestamp": 1589001049133
            },
            "posted": {
                "date-parts": [[2020, 2, 13]]
            }, 
            "group-title": "Genomics", 
            "reference-count": 95, 
            "publisher": "Cold Spring Harbor Laboratory", 
            "content-domain": {
                "domain": [], 
                "crossmark-restriction": "False"
            }, 
            "accepted": {
                "date-parts": [[2020, 5, 5]]
            }, 
            "abstract": "...",
            "DOI": "10.1101/2020.02.12.944629",
            "type": "posted-content", 
            "created": {
                "date-parts": [[2020, 2, 14]], 
                "date-time": "2020-02-14T05:35:26Z", 
                "timestamp": 1581658526000
            }, 
            "source": "Crossref", 
            "is-referenced-by-count": 0, 
            "title": "Retrocopying expands the functional repertoire of APOBEC3 antiviral proteins in primates", 
            "prefix": "10.1101", 
            "author": [
                {
                    "ORCID": "http://orcid.org/0000-0001-9284-1744", 
                    "authenticated-orcid": "False", 
                    "given": "Lei", 
                    "family": "Yang", 
                    "sequence": "first", "affiliation": []
                },
                {
                    "given": "Michael", "family": "Emerman", "sequence": "additional", "affiliation": []
                }, 
                {
                    "given": "Harmit S.", "family": "Malik", "sequence": "additional", "affiliation": []
                }, 
                {
                    "ORCID": "http://orcid.org/0000-0003-0950-2253", "authenticated-orcid": "False", "suffix": "Jr.", "given": "Richard N.", "family": "McLaughlin", "sequence": "additional", "affiliation": []
                }
            ], 
            "member": "246", 
            "reference": [
                {"key": "2020050808162359000_2020.02.12.944629v2.1", "DOI": "10.3389/fmicb.2012.00275", "doi-asserted-by": "publisher"}
            ],
            "container-title": [], 
            "original-title": [], 
            "link": [
                {
                    "URL": "https://syndication.highwire.org/content/doi/10.1101/2020.02.12.944629", 
                    "content-type": "unspecified", 
                    "content-version": "vor", 
                    "intended-application": "similarity-checking"
                }
            ], 
            "deposited": {
                "date-parts": [[2020, 5, 8]], 
                "date-time": "2020-05-08T15:16:34Z", 
                "timestamp": 1588950994000
            }, 
            "score": 1.0, 
            "subtitle": [], 
            "short-title": [], 
            "issued": {
                "date-parts": [[2020, 2, 13]]
            }, 
            "references-count": 95, 
            "URL": "http://dx.doi.org/10.1101/2020.02.12.944629", 
            "relation": {"cites": []}, 
            "subtype": "preprint"
        }
        expected_node = TestJSONNode(
            label='Article',
            properties={'article_type': 'preprint', 'doi': '10.1101/2020.02.12.944629', 'journal_title': 'bioRxiv', 'publication_date': '2020-02-13', 'title': 'Retrocopying expands the functional repertoire of APOBEC3 antiviral proteins in primates', 'abstract': '...', 'position_idx': 0},
            children={
                'has_author': [
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Lei', 'surname': 'Yang', 'collab': '', 'position_idx': 0},
                        children={
                            'has_orcid': [
                                TestJSONNode(
                                    label='Contrib_id',
                                    properties={'text': 'http://orcid.org/0000-0001-9284-1744', 'position_idx': 0},
                                ),
                            ],
                        },
                    ),
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Michael', 'surname': 'Emerman', 'collab': '', 'position_idx': 1},
                        children={
                            'has_orcid': [],
                        },
                    ),
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Harmit S.', 'surname': 'Malik', 'collab': '', 'position_idx': 2},
                        children={
                            'has_orcid': [],
                        },
                    ),
                    TestJSONNode(
                        label='Contrib',
                        properties={'given_names': 'Richard N.', 'surname': 'McLaughlin', 'collab': '', 'position_idx': 3},
                        children={
                            'has_orcid': [
                                TestJSONNode(
                                    label='Contrib_id',
                                    properties={'text': 'http://orcid.org/0000-0003-0950-2253', 'position_idx': 0},
                                ),
                            ],
                        },
                    ),
                ],
                'has_figure': [
                    TestJSONNode(
                        label='Fig',
                        properties={'label': 'not available', 'caption': 'not available', 'title': 'not available', 'graphic': '', 'position_idx': 0},
                    ),
                ],
            }
        )
        actual_node = JSONNode(input, CROSSREF_PREPRINT_API_GRAPH_MODEL)
        self.assert_nodes_equal(expected_node, actual_node)


class TestXMLNode(TestJSONNode):
    def __init__(self, label: str, properties: dict, children: dict = {}, namespaces: dict = None):
        super().__init__(label, properties, children=children)
        self.namespaces = namespaces


class XMLNodeTestCase(NodeTestCase):

    def assert_nodes_equal(self, expected: XMLNode, actual: XMLNode):
        if expected.namespaces is None:
            self.assertIsNone(actual.namespaces)
        else:
            self.assertDictEqual(expected.namespaces, actual.namespaces)
        super().assert_nodes_equal(expected, actual)

    def test_jats(self):
        input = b'''<?xml version="1.0" encoding="UTF-8"?>
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
                    <article-categories>
                        <subj-group subj-group-type="author-type">
                            <subject>Regular Article</subject>
                        </subj-group>
                        <subj-group subj-group-type="heading">
                            <subject>New Results</subject>
                        </subj-group>
                        <subj-group subj-group-type="hwp-journal-coll">
                            <subject>Microbiology</subject>
                        </subj-group>
                    </article-categories>
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
        expected_node = TestXMLNode(
            label='Article',
            properties={'article_type': 'article', 'doi': '10.1101/2020.03.02.972935', 'version': '1.1', 'title': 'Isolation \'and\' "characterization"  $of {SARS-CoV-2} from Hôpital Bichat the first \\US COVID-19 patient', 'position_idx': 0},
            children={
                'has_author': [
                    TestXMLNode(
                        label='Contrib',
                        properties={'given_names': 'Chuang', 'surname': 'Liu', 'position_idx': 0},
                        children={
                            'has_orcid': [
                                TestXMLNode(
                                    label='Contrib_id',
                                    properties={'text': 'http://orcid.org/0000-0002-1012-2226', 'position_idx': 0},
                                ),
                            ],
                        },
                    ),
                    TestXMLNode(
                        label='Contrib',
                        properties={'given_names': 'Yang', 'surname': 'Yang', 'position_idx': 1},
                        children={
                            'has_orcid': [],
                        },
                    ),
                ],
                'has_figure': [
                    TestXMLNode(
                        label='Fig',
                        properties={'label': 'Figure 3', 'caption': 'This is nice.', 'graphic': 'http://this.com/figure/3', 'position_idx': 0},
                    ),
                ],
                'has_subject': [
                    TestXMLNode(
                        label='Subject',
                        properties={'text': 'Microbiology', 'position_idx': 0},
                    ),
                ],
            }
        )
        actual_node = XMLNode(parse(BytesIO(input)).getroot(), JATS_GRAPH_MODEL)
        self.assert_nodes_equal(expected_node, actual_node)