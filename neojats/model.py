JATS_GRAPH_MODEL = {
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