from lxml.etree import Element
from neotools.utils import inner_text

NS = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'obo': 'http://purl.obolibrary.org/obo/',
    'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'dc': 'http://purl.org/dc/elements/1.1/',
}

OWL = "{%s}" % NS['owl']
OBO = "{%s}" % NS['obo']
OBOINOWL = "{%s}" % NS['oboInOwl']
RDF = "{%s}" % NS['rdf']
RDFS = "{%s}" % NS['rdfs']
DC = "{%s}" % NS['dc']


# need a function factory to determin which attribute to get the value from
def get_attr_factory(key, default=None):
    def f(e: Element):
        return e.get(key, default)
    return f


# simple
def get_text(e: Element):
    return e.text or ''


def get_inner_text(e: Element):
    return inner_text(e)


# format of the graph model
# Dict(
# 'Xpath': <XPath expression to find the target element
# 'properties: Dict(<the name of the node's property>, Tuple(<xpath to the element that contains the value>, <a function to extract the value from the target element>))
# 'children: Dict(<relationship to the children nodes>, <graph model for the children>)
# )

# <!-- http://purl.obolibrary.org/obo/DOID_9976 -->
#    <owl:Ontology rdf:about="http://purl.obolibrary.org/obo/doid.owl">
#         <owl:versionIRI rdf:resource="http://purl.obolibrary.org/obo/doid/releases/2020-04-20/doid.owl"/>
#         <owl:imports rdf:resource="http://purl.obolibrary.org/obo/doid/obo/ext.owl"/>
#         <dc:description rdf:datatype="http://www.w3.org/2001/XMLSchema#string">The Disease Ontology has been developed as a standardized ontology for human disease with the purpose of providing the biomedical community with consistent, reusable and sustainable descriptions of human disease terms, phenotype characteristics and related medical vocabulary disease concepts.</dc:description>
#         <dc:title rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Human Disease Ontology</dc:title>
#         <terms:license rdf:resource="https://creativecommons.org/publicdomain/zero/1.0/"/>
#         <oboInOwl:date rdf:datatype="http://www.w3.org/2001/XMLSchema#string">20:04:2020 16:19</oboInOwl:date>
#         <oboInOwl:default-namespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">disease_ontology</oboInOwl:default-namespace>
#         <oboInOwl:hasOBOFormatVersion rdf:datatype="http://www.w3.org/2001/XMLSchema#string">1.2</oboInOwl:hasOBOFormatVersion>
#         <oboInOwl:saved-by rdf:datatype="http://www.w3.org/2001/XMLSchema#string">lschriml</oboInOwl:saved-by>
#         <rdfs:comment rdf:datatype="http://www.w3.org/2001/XMLSchema#string">The Disease Ontology content is available via the Creative Commons Public Domain Dedication CC0 1.0 Universal license (https://creativecommons.org/publicdomain/zero/1.0/).</rdfs:comment>
#    </owl:Ontology>
# <owl:Class rdf:about="http://purl.obolibrary.org/obo/DOID_9976">
#     <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/DOID_2559"/>
#     <obo:IAO_0000115 rdf:datatype="http://www.w3.org/2001/XMLSchema#string">An opiate dependence that involves the continued use of heroin despite problems related to use of the substance.</obo:IAO_0000115>
#     <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">MESH:D006556</oboInOwl:hasDbXref>
#     <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">NCI:C34694</oboInOwl:hasDbXref>
#     <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">SNOMEDCT_US_2019_09_01:231477003</oboInOwl:hasDbXref>
#     <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">UMLS_CUI:C0019337</oboInOwl:hasDbXref>
#     <oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">disease_ontology</oboInOwl:hasOBONamespace>
#     <oboInOwl:id rdf:datatype="http://www.w3.org/2001/XMLSchema#string">DOID:9976</oboInOwl:id>
#     <oboInOwl:inSubset rdf:resource="http://purl.obolibrary.org/obo/doid#NCIthesaurus"/>
#     <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">heroin dependence</rdfs:label>
# </owl:Class>
# <owl:Axiom>
#     <owl:annotatedSource rdf:resource="http://purl.obolibrary.org/obo/DOID_9976"/>
#     <owl:annotatedProperty rdf:resource="http://purl.obolibrary.org/obo/IAO_0000115"/>
#     <owl:annotatedTarget rdf:datatype="http://www.w3.org/2001/XMLSchema#string">An opiate dependence that involves the continued use of heroin despite problems related to use of the substance.</owl:annotatedTarget>
#     <dc:type rdf:resource="http://purl.obolibrary.org/obo/ECO_0007638"/>
#     <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">url:http://en.wikipedia.org/wiki/Opioid_dependence</oboInOwl:hasDbXref>
# </owl:Axiom>
# <oboInOwl:hasExactSynonym


OBO_GRAPH_MODEL = {
    'XPath': 'rdf:RDF',
    'properties': {
        'version': ('owl:versionIRI', get_attr_factory(RDF+'resource')),
    },
    'children': {
        'classes': {
            'XPath': 'owl:Class',
            'properties': {
                'about': ('.', get_attr_factory(RDF+'about')),
                'definition': ('obo:IAO_0000115', get_text),
                'exact_synonyms': ('oboInOwl:hasExactSynonym', get_text),
                'hasRelatedSynonym': ('oboInOwl:hasRelatedSynonym', get_text), 
                'owl_id': ('oboInOwl:id', get_text),
                'owl_label': ('rdfs:label', get_text),
                'subClassOf': ('rdfs:subClassOf', get_attr_factory(RDF+'resource'), 'as_list'),
                'deprecated': ('owl:deprecated', get_text),
            }
        },
    },
}

DOID_GRAPH_MODEL = OBO_GRAPH_MODEL

UBERON_GRAPH_MODEL = OBO_GRAPH_MODEL

GO_GRAPH_MODEL = OBO_GRAPH_MODEL

CHEBI_GRAPH_MODEL = OBO_GRAPH_MODEL

CL_GRAPH_MODEL = OBO_GRAPH_MODEL

OBI_GRAPH_MODEL = OBO_GRAPH_MODEL

BAO_GRAPH_MODEL = OBO_GRAPH_MODEL


# CELLOSAURUS

# <cell-line category="Hybridoma" created="2013-02-11" last_updated="2019-05-24" entry_version="5">
#   <accession-list>
#     <accession type="primary">CVCL_G217</accession>
#   </accession-list>
#   <name-list>
#     <name type="identifier">(BF1) 8A3.31</name>
#   </name-list>
#   <comment-list>
#     <comment category="Monoclonal antibody target">
#       <xref-list>
#         <xref database="UniProtKB" category="Sequence databases" accession="P05067">
#           <property-list>
#             <property name="gene/protein designation" value="Human APP (binds to APP42)"/>
#           </property-list>
#           <url><![CDATA[https://www.uniprot.org/uniprot/P05067]]></url>
#         </xref>
#       </xref-list>
#     </comment>
#     <comment category="Monoclonal antibody isotype"> IgG1 </comment>
#   </comment-list>
#   <species-list>
#     <cv-term terminology="NCBI-Taxonomy" accession="10090">Mus musculus</cv-term>
#   </species-list>
#   <reference-list>
#     <reference resource-internal-ref="Patent=US4845026"/>
#   </reference-list>
#   <xref-list>
#     <xref database="CLO" category="Ontologies" accession="CLO_0001019">
#       <url><![CDATA[https://www.ebi.ac.uk/ols/ontologies/clo/terms?iri=http://purl.obolibrary.org/obo/CLO_0001019]]></url>
#     </xref>
#     <xref database="ATCC" category="Cell line collections" accession="HB-9283">
#       <url><![CDATA[https://www.atcc.org/Products/All/HB-9283.aspx]]></url>
#     </xref>
#     <xref database="Wikidata" category="Other" accession="Q54422077">
#       <url><![CDATA[https://www.wikidata.org/wiki/Q54422077]]></url>
#     </xref>
#   </xref-list>
# </cell-line>

CVCL_GRAPH_MODEL = {
    'XPath': 'Cellosaurus',
    'properties': {
        'description': ('header/description', get_text),
    },
    'children': {
        'classes': {
            'XPath': 'cell-line-list/cell-line',
            'properties': {
                'category': ('.', get_attr_factory('category')),
                'sex': ('.', get_attr_factory('sex')),
                'species': ('species-list', get_text, 'is_list'),
                'accession': ('accession-list/accession[@type="primary"]', get_text),
                'name-list': ('name-list', get_text, 'is_list'),
                'subClassOf': ('derived-from/cv-term', get_attr_factory('accession'), 'is_list'),
            }
        }

    }
}


# UNIPROT_GRAPH_MODEL
# <entry dataset="Swiss-Prot" created="2011-06-28" modified="2020-02-26" version="33" xmlns="http://uniprot.org/uniprot">
#   <accession>Q6GZX1</accession>
#   <name>004R_FRG3G</name>
#   <protein>
#     <recommendedName>
#       <fullName>Uncharacterized protein 004R</fullName>
#     </recommendedName>
#   </protein>
#   <gene>
#     <name type="ORF">FV3-004R</name>
#   </gene>
#   <organism>
#     <name type="scientific">Frog virus 3 (isolate Goorha)</name>
#     <name type="common">FV-3</name>
#     <dbReference type="NCBI Taxonomy" id="654924"/>
#     <lineage>
#       <taxon>Viruses</taxon>
#       <taxon>Iridoviridae</taxon>
#       <taxon>Alphairidovirinae</taxon>
#       <taxon>Ranavirus</taxon>
#     </lineage>
#   </organism>
#   <organismHost>
#     <name type="scientific">Dryophytes versicolor</name>
#     <name type="common">chameleon treefrog</name>
#     <dbReference type="NCBI Taxonomy" id="30343"/>
#   </organismHost>
#   <organismHost>
#     <name type="scientific">Lithobates pipiens</name>
#     <name type="common">Northern leopard frog</name>
#     <name type="synonym">Rana pipiens</name>
#     <dbReference type="NCBI Taxonomy" id="8404"/>
#   </organismHost>
#   <organismHost>
#     <name type="scientific">Lithobates sylvaticus</name>
#     <name type="common">Wood frog</name>
#     <name type="synonym">Rana sylvatica</name>
#     <dbReference type="NCBI Taxonomy" id="45438"/>
#   </organismHost>
#   <organismHost>
#     <name type="scientific">Notophthalmus viridescens</name>
#     <name type="common">Eastern newt</name>
#     <name type="synonym">Triturus viridescens</name>
#     <dbReference type="NCBI Taxonomy" id="8316"/>
#   </organismHost>
#   <reference key="1">
#     <citation type="journal article" date="2004" name="Virology" volume="323" first="70" last="84">
#       <title>Comparative genomic analyses of frog virus 3, type species of the genus Ranavirus (family Iridoviridae).</title>
#       <authorList>
#         <person name="Tan W.G."/>
#         <person name="Barkman T.J."/>
#         <person name="Gregory Chinchar V."/>
#         <person name="Essani K."/>
#       </authorList>
#       <dbReference type="PubMed" id="15165820"/>
#       <dbReference type="DOI" id="10.1016/j.virol.2004.02.019"/>
#     </citation>
#     <scope>NUCLEOTIDE SEQUENCE [LARGE SCALE GENOMIC DNA]</scope>
#   </reference>
#   <comment type="subcellular location">
#     <subcellularLocation>
#       <location evidence="2">Host membrane</location>
#       <topology evidence="2">Single-pass membrane protein</topology>
#     </subcellularLocation>
#   </comment>
#   <dbReference type="EMBL" id="AY548484">
#     <property type="protein sequence ID" value="AAT09663.1"/>
#     <property type="molecule type" value="Genomic_DNA"/>
#   </dbReference>
#   <dbReference type="RefSeq" id="YP_031582.1">
#     <property type="nucleotide sequence ID" value="NC_005946.1"/>
#   </dbReference>
#   <dbReference type="GeneID" id="2947776"/>
#   <dbReference type="KEGG" id="vg:2947776"/>
#   <dbReference type="Proteomes" id="UP000008770">
#     <property type="component" value="Genome"/>
#   </dbReference>
#   <dbReference type="GO" id="GO:0033644">
#     <property type="term" value="C:host cell membrane"/>
#     <property type="evidence" value="ECO:0000501"/>
#     <property type="project" value="UniProtKB-SubCell"/>
#   </dbReference>
#   <dbReference type="GO" id="GO:0016021">
#     <property type="term" value="C:integral component of membrane"/>
#     <property type="evidence" value="ECO:0000501"/>
#     <property type="project" value="UniProtKB-KW"/>
#   </dbReference>
#   <proteinExistence type="predicted"/>
#   <keyword id="KW-1043">Host membrane</keyword>
#   <keyword id="KW-0472">Membrane</keyword>
#   <keyword id="KW-1185">Reference proteome</keyword>
#   <keyword id="KW-0812">Transmembrane</keyword>
#   <keyword id="KW-1133">Transmembrane helix</keyword>
#   <feature type="chain" id="PRO_0000410528" description="Uncharacterized protein 004R">
#     <location>
#       <begin position="1"/>
#       <end position="60"/>
#     </location>
#   </feature>
#   <feature type="transmembrane region" description="Helical" evidence="1">
#     <location>
#       <begin position="14"/>
#       <end position="34"/>
#     </location>
#   </feature>
#   <evidence type="ECO:0000255" key="1"/>
#   <evidence type="ECO:0000305" key="2"/>
#   <sequence length="60" mass="6514" checksum="12F072778EE6DFE4" modified="2004-07-19" version="1">MNAKYDTDQGVGRMLFLGTIGLAVVVGGLMAYGYYYDGKTPSSGTSFHTASPSFSSRYRY</sequence>
# </entry>

UNIPROT_GRAPH_MODEL = {
    'XPath': 'uniprot',
    'children': {
        'classes': {
            'XPath': 'default:entry[@dataset="Swiss-Prot"]',
            'properties': {
                'accession': ('default:accession', get_text),
                'name': ('default:name', get_text),
                'proteinname': ('default:protein/default:recommendedName/default:fullName', get_text),
                'genename': ('default:gene/default:name', get_text),
                'organism': ('default:organism/default:dbReference[@type="NCBI Taxonomy"]', get_attr_factory('id'), 'as_list'),
                'geneID': ('default:dbReference[@type="GeneID"]', get_attr_factory('id')),
                'sequence': ('default:sequence', get_text),
                'go': ('default:bReference[@type="GO"]', get_attr_factory('id'), 'as_list'),
                'keywords': ('default:keyword', get_text, 'as_list')
            }
        }
    }
}


# TAXONOMY
# <owl:Class rdf:about="http://purl.obolibrary.org/obo/NCBITaxon_1000034">
#         <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/NCBITaxon_2622719"/>
#         <ncbitaxon:has_rank rdf:resource="http://purl.obolibrary.org/obo/NCBITaxon_species"/>
#         <oboInOwl:hasDbXref rdf:datatype="http://www.w3.org/2001/XMLSchema#string">GC_ID:11</oboInOwl:hasDbXref>
#         <oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">ncbi_taxonomy</oboInOwl:hasOBONamespace>
#         <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Erwinia sp. Koakin</rdfs:label>
# </owl:Class>


NCBITAXON_GRAPH_MODEL = {
    'XPath': 'rdf:RDF',
    'properties': {
        'version': ('owl:versionIRI', get_attr_factory(RDF+'resource')),
    },
    'children': {
        'classes': {
            'XPath': 'owl:Class',
            'properties': {
                'about': ('.', get_attr_factory(RDF+'about')),
                'owl_label': ('rdfs:label', get_text),
                'rank': ('ncbitaxon:has_rank', get_attr_factory(RDF+'resource')),
                'subClassOf': ('rdfs:subClassOf', get_attr_factory(RDF+'resource'), 'as_list'),
            }
        },
    },
}
