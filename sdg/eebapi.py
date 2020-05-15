import argparse
import json
from .sdnode import SDNode, API
from smtag.predict.cartridges import CARTRIDGE
from smtag.predict.engine import SmtagEngine
from . import EEB_PUBLIC_API


GET_COLLECTION = "collection/"
GET_ARTICLE = "doi/"
GET_FIGURE = "figure"

TAGGING_ENGINE = SmtagEngine(CARTRIDGE)


def tag_it(text, format):
    tags = TAGGING_ENGINE.tag(text, 'sd-tag', format)
    if format == 'json':
        tags = json.loads(tags[0])
        tags = tags['smtag'][0]['entities']
    return tags


class SDCollection(SDNode):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name
        children = []
        for d in data:
            doi = d.get('doi', None)
            if doi:
                children.append(doi)
            else:
                import pdb; pdb.set_trace()
        self.children = children

    def __len__(self):
        return len(self.children)


class SDArticle(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.get('title', '')
        self.journal = self.get('journal', '')
        self.doi = self.get('doi', '')
        self.nb_figures = int(self.get('nb_figures', 0))  # remember to change this in sdg!
        self.add_properties({
            'doi': self.doi,
            'title': self.title,
            'journalName': self.journal,
            'nb_figures': self.nb_figures
        })
        self.children = range(self.nb_figures)


class SDFigure(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.paper_doi = self.get('doi', '')
        self.fig_label = self.get('fig_label', '')
        self.fig_title = self.get('fig_title', '')
        self.caption = self.get('caption', '')
        self.add_properties({
            'fig_label': self.fig_label,
            'title': self.fig_title,
            'caption': self.caption,
        })
        self.children = [SDPanel(self)]  # provisional until we fix automatic panelization in general case


class SDPanel(SDNode):
    def __init__(self, fig: SDFigure):
        super().__init__(fig._data)
        self.paper_doi = fig.paper_doi
        self.fig_label = fig.fig_label  # correct typo in sdg!!
        self.panel_label = 'A' # provisional until we get automatic panelization
        self.panel_id = ":".join([self.paper_doi, self.fig_label, self.panel_label])
        self.caption = fig.get('caption', '')
        if self.caption:
            self.formatted_caption = tag_it(fig.caption, format='xml')
        else:
            self.formatted_caption = ''
        self.add_properties({
            "paper_doi": self.paper_doi,
            "fig_label": self.fig_label,
            "panel_id": self.panel_id,
            "panel_label": self.panel_label,
            "caption": self.caption, 
            "formatted_caption": self.formatted_caption
        })
        if self.caption:
            self.children = tag_it(self.caption, format='json')
        else:
            self.children = []


class SDTag(SDNode):
    def __init__(self, data):
        super().__init__(data)
        category = self.get('category', None)
        if category is None:
            self.category = 'entity'
        elif category is None:
            self.category = ''
        else:
            self.category = category
        self.category_score = self.get('category_score', '')
        self.type = self.get('type', '')
        self.type_score = self.get('type_score', '')
        self.role = self.get('role', '')
        self.role_score = self.get('role_score', '')
        self.text = self.get('text', '')
        self.add_properties({
            'category': self.category, 
            'category_score': self.category_score,
            'type': self.type, 
            'type_score': self.type_score,
            'role': self.role, 
            'role_score': self.role_score,
            'text': self.text,
        })


class EEBAPI(API):

    def collection(self, collection_name):
        url = EEB_PUBLIC_API + GET_COLLECTION + collection_name
        data = self.rest2data(url)
        article_list = SDCollection(data, collection_name)
        return article_list

    def article(self, doi):
        url = EEB_PUBLIC_API + GET_ARTICLE + doi
        data = self.rest2data(url)
        if data:
            article = SDArticle(data)  # most recent version should be first item in list
        else:
            article = None
        return article

    def figure(self, figure_index=0, doi=''):
        params = {'doi': doi, 'position_idx': figure_index}
        url = EEB_PUBLIC_API + GET_FIGURE
        data = self.rest2data(url, params)
        if data:
            figure = SDFigure(data)
        else:
            figure = None
        return figure

    def panel(self, panel: SDPanel):
        # placeholder until we have automated panelization going
        return panel

    def tag(self, data):
        # because tags are only accessible through a figure, there is no request to the API
        # the data is provided directly and obtained from prior request figure(doi, position_idx).children
        if data:
            tag = SDTag(data)
        else:
            tag = None
        return tag

    def __len__(self):
        return self.N


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="interace to the SourceData API" )
    parser.add_argument('-L', '--listing', action="store_true", help="List of articles in the collection.") 
    parser.add_argument('-D', '--doi', default='', help="Takes a doi and return article information")
    parser.add_argument('-F', '--figure', default='', help="Takes the figure index and returns the figure legend for the figure in the paper specified with the --doi option") 
    args = parser.parse_args()
    listing = args.listing
    doi_arg = args.doi
    fig = args.figure
    collection_name = 'covid19'
    eebapi = EEBAPI()

    collection = eebapi.collection(collection_name)
    print(f"Collection {collection.name} has {len(collection)} articles.")

    if listing:
        for doi in collection.children:
            a = eebapi.article(doi)
            print(f"{doi}: {a.title}")

    if doi_arg:
        article = eebapi.article(doi_arg)
        print('doi:', article.doi)
        print('title:', article.title)
        print('journal:', article.journal)
        print('number of figures:', article.nb_figures)

    if fig and doi_arg:
        figure = eebapi.figure(fig, doi_arg)
        print("label:", figure.fig_label)
        print("caption:", figure.caption)
        for panel in figure.children:
            print(f"pseudo panel {panel.panel_id}")
            print(f"formatted tagged caption:", panel.formatted_caption)
            for t in panel.children:
                sd_tag = SDTag(t)
                print(sd_tag.properties)
