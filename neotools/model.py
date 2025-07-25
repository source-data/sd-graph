import re
from lxml.etree import Element
from neotools.utils import inner_text
from datetime import date


# need a function factory to determin which attribute to get the value from
def get_attr_factory(key, default=None):
    def f(e: Element):
        return e.get(key, default)
    return f


# pedandic version, allows to modulate the default value
def get_text_factory(default=''):
    def f(e: Element):
        return e.text or default
    return f


# simpler, less typing
def get_text(e: Element):
    return e.text or ''


def get_inner_text(e: Element):
    return inner_text(e)


def get_inner_text_without_sup_xref(e: Element):
    # remove <sup><xref ref-type="bibr" rid="c1">1</xref></sup>
    sup_xref_elements = e.xpath('.//sup/xref')
    for sup_xref in sup_xref_elements:
        sup_xref.getparent().remove(sup_xref)
    return get_inner_text(e)


def get_abstract_text(e: Element):
    text = " ".join([get_inner_text_without_sup_xref(p) for p in e.xpath('.//p')])
    return text


def get_datetime(e: Element):
    # datetime('2015-06-24T12:50:35.556+0100')
    # <date date-type="accepted">
    # <day>28</day>
    # <month>2</month>
    # <year>2020</year>
    # </date>
    day = e.xpath('day/text()')[0]
    month = e.xpath('month/text()')[0]
    year = e.xpath('year/text()')[0]
    return f"{year}-{month}-{day}"


def get_caption(e: Element):
    title = e.xpath('title')
    paragraphs = e.xpath('p')
    if title:
        caption = ""
        for p in paragraphs:
            caption += inner_text(p)
            tail = p.tail or ''
            caption += tail
    else:
        caption = get_inner_text_without_sup_xref(e)
    return caption


# format of the graph model
# Dict(
# 'Xpath': <XPath expression to find the target element
# 'properties: Dict(<the name of the node's property>, Tuple(<xpath to the element that contains the value>, <a function to extract the value from the target element>))
# 'children: Dict(<relationship to the children nodes>, <graph model for the children>)
# )


# <article-categories>
# <subj-group subj-group-type="author-type">
# <subject>Regular Article</subject>
# </subj-group>
# <subj-group subj-group-type="heading">
# <subject>New Results</subject>
# </subj-group>
# <subj-group subj-group-type="hwp-journal-coll">
# <subject>Microbiology</subject>
# </subj-group>
# </article-categories>

JATS_GRAPH_MODEL = {
    'XPath': 'article',
    'properties': {
        'article-type': ('.', get_attr_factory('article-type')),
        'journal-title': ('front/journal-meta/journal-title-group/journal-title', get_text),
        'doi': ('front/article-meta/article-id[@pub-id-type="doi"]', get_text),
        'version': ('front/article-meta/article-version', get_text),
        'title': ('front/article-meta/title-group/article-title', get_inner_text),
        'abstract': ('front/article-meta/abstract/p|front/article-meta/abstract', get_abstract_text),
        'publication-date': ('front/article-meta/history/date[@date-type="accepted"]', get_datetime),
    },
    'children': {
        'has_author': {
            'XPath': '''front/article-meta/contrib-group/contrib[@contrib-type="author"]''',
            'properties': {
                'given_names': ('name/given-names', get_text),
                'surname': ('name/surname', get_text),
                'collab': ('collab', get_text),
                'corresp': ('.', get_attr_factory('corresp')),
            },
            'children': {
                'has_orcid': {
                    'XPath': 'contrib-id[@contrib-id-type="orcid"]',
                }
            }
        },
        'has_figure': {
            'XPath': './/fig',
            'properties': {
                'label': ('label', get_text),
                'caption': ('caption', get_caption),
                'title': ('caption/title', get_inner_text),
                'graphic': ('graphic', get_attr_factory('{http://www.w3.org/1999/xlink}href')),
            },
        },
        'has_subject': {
            'XPath': 'front/article-meta/article-categories/subj-group[@subj-group-type="hwp-journal-coll"]/subject',
            'properties': {}  # text property by default
        }
    }
}


CORD19_GRAPH_MODEL = {
    'path': {
        'type': 'article', 
        'funct': lambda d: d['article']
    },
    'properties': {
        'doi': lambda d: d['metadata']['doi'],
        'pub_date': lambda d: d['metadata']['pub_date'],
        'title': lambda d: d['metadata']['title'],
        'abstract': lambda d: ' '. join([para['text'] for para in d['abstract']]),
    },
    'children': {
        'has_author': {
            'path': {
                'type': 'Contrib',  # to harmonize with JATS model
                'funct': lambda d: d['metadata']['authors']
            },
            'properties': {
                'given_names': lambda d: d['first'],
                'surname': lambda d: d['last'],
            },
        },
        'has_figure': {
            'path': {
                'type': 'fig',
                'funct': lambda d: [{key: val} for key, val in d['ref_entries'].items() if val['type'] == 'figure']
            },
            'properties': {
                'label': lambda d: list(d)[0],
                'caption': lambda d: list(d.values())[0]['text'],
            },
        },
    }
}


# BIORXIV_API_GRAPH_MODEL = {
#     'path': {
#         'type': 'article',
#         'funct': lambda d: d['article']
#     },
#     'properties': {
#         'article-type': lambda d: 'preliminary',
#         'doi': lambda d: d['doi'],
#         'journal-title': lambda d: 'bioRxiv',
#         'publication-date': lambda d: d['date'],
#         'title': lambda d: d['title'],
#         'abstract': lambda d: d['abstract'],
#         'version': lambda d: d['version']
#     },
#     'children': {
#         'has_author': {
#             'path': {
#                 'type': 'author', 
#                 'funct': lambda d: d['authors'].split(';')
#             },
#             'properties': {
#                 'given_names': lambda text: text.split(',')[1].strip(),
#                 'surname': lambda text: text.split(',')[0],
#             },
#         }
#     }
# }


CROSSREF_PREPRINT_API_GRAPH_MODEL = {
    'path': {
        'type': 'article',
        'funct': lambda d: d['article']
    },
    'properties': {
        'article-type': lambda d: d.get('subtype', 'unknown'),
        'doi': lambda d: d['DOI'],
        'journal-title': lambda d: d['institution'][0]['name'] if 'institution' in d else '',  # for obscure reasons; journal would be d['container-title']
        'publication-date': lambda d: date(*d['posted']['date-parts'][0]).isoformat() if 'posted' in d else '',  # journal: d['ublished-online']['date-parts']
        'title': lambda d: d['title'],
        'abstract': lambda d: d.get('abstract', ''),  # contains jats namespaced formatting tags
    },
    'children': {
        'has_author': {
            'path': {
                'type': 'Contrib',  # to harmonize with JATS model
                'funct': lambda d: d['author']
            },
            'properties': {
                'given_names': lambda d: d.get('given', ''),
                'surname': lambda d: d.get('family', ''),
                'collab': lambda d: d.get('name', ''),  # consortium
            },
            'children': {
                'has_orcid': {
                    'path': {
                        'type': 'contrib-id',
                        'funct': lambda d: [d.get('ORCID')] if d.get('ORCID', False) else [],
                    },
                    'properties': {
                        'text': lambda text: text
                    }
                },
            },
        },
        'has_figure': {
            'path': {
                'type': 'fig',
                'funct': lambda d: [{'label': 'not available', 'caption': 'not available', 'title': 'not available', 'graphic': ''}]
            },
            'properties': {
                'label': lambda d: d.get('label', ''),
                'caption': lambda d: d.get('caption', ''),
                'title': lambda d: d.get('title', ''),
                'graphic': lambda d: d.get('graphic', ''),
            },
        }
    }
}


RESPONSE_REGEX_RRC19 = re.compile(r'^review (\d):', re.IGNORECASE)


def get_review_idx_from_title(d):
    m = RESPONSE_REGEX_RRC19.match(d['title'][0])
    if m:
        idx = m.group(1)
    else:
        idx = ''
    return idx


def get_type(d):
    node_type = 'Unknown'
    info = d.get('review', '')
    if info:
        type_info = info.get('type','')
        if type_info == 'author-comment':
            node_type = 'Response'
        elif type_info == 'editor-report':
            node_type = 'PeerReviewMaterial' 
        elif type_info == 'referee-report':
            node_type = 'Review'
        else:
            node_type = 'PeerReviewMaterial'
    return node_type


CROSSREF_PEERREVIEW_GRAPH_MODEL = {
    'path': {
        'type': lambda d: get_type(d),
        'funct': lambda d: d['article']
    },
    'properties': {
        'doi': lambda d: d['DOI'],
        'reviewed_by': lambda d: d['publisher'],
        'posting_date': lambda d: date(*d['published-print']['date-parts'][0]).isoformat(),  # journal: d['ublished-online']['date-parts']
        'highlight': lambda d: d['title'][0],
        'related_article_doi': lambda d: d['relation']['is-review-of'][0]['id'],
        'review_idx': lambda d: get_review_idx_from_title(d),
        'text': lambda x: '',
    },
    'children': {
        'has_licence': {
            'path': {
                'type': 'licence',
                'funct': lambda d: d.get('license', [])
            },
            'properties': {
                'url': lambda d: d.get('URL', '')
            },
        }
    }
}


def get_posting_date(d):
    published = d.get('published-online', {}).get('date-parts', [])
    if published:
        return date(*published[0]).isoformat()
    published = d.get('published-print', {}).get('date-parts', [])
    if published:
        return date(*published[0]).isoformat()
    else:
        return ''


CROSSREF_PCI_REVIEW_GRAPH_MODEL = {
    'path': {
        'type': 'PeerReviewMaterial',
        'funct': lambda d: d['article']
    },
    'properties': {
        'doi': lambda d: d['DOI'],
        'reviewed_by': lambda d: d['publisher'],
        'posting_date': lambda d: get_posting_date(d),
        'highlight': lambda d: d['title'][0],
        'related_article_doi': lambda d: d['relation']['is-review-of'][0]['id'],
        'review_idx': lambda d: '0',
        'text': lambda d: ''
    },
    'children': {
        'has_licence': {
            'path': {
                'type': 'licence',
                'funct': lambda d: d.get('license', []),
            },
            'properties': {
                'url': lambda d: d.get('URL', ''),
            },
        }
    }
}