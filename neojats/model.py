from lxml.etree import Element
from neotools.utils import inner_text


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


JATS_GRAPH_MODEL = {
    'XPath': 'article',
    'properties': {
        'article-type': ('.', get_attr_factory('article-type')),
        'doi': ('front/article-meta/article-id[@pub-id-type="doi"]', get_text),
        'version': ('front/article-meta/article-version', get_text),
        'title': ('front/article-meta/title-group/article-title', get_inner_text),
        'abstract': ('front/article-meta/abstract/p', get_inner_text_without_sup_xref),
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
    }
}
