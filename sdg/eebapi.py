import argparse
import json
from lxml.etree import fromstring
from neotools.utils import inner_text
from .sdnode import (
    SDNode, API,
    BaseCollection, BaseArticle, BaseFigure, BasePanel, BaseTag
)
from smtag.predict.cartridges import CARTRIDGE
from smtag.predict.engine import SmtagEngine
from neotools.utils import cleanup
from . import EEB_PUBLIC_API


TAGGING_ENGINE = SmtagEngine(CARTRIDGE)


def tag_it(text, format='xml'):
    text = cleanup(text)
    tags = TAGGING_ENGINE.smtag(text, 'sd-tag', format)[0] # a single example is submitted to the engine
    if format == 'json':
        tags = json.loads(tags)
        tags = tags['smtag']
    return tags


def xml2json(xml_str:str):
    e = fromstring(xml_str)
    panels = e.xpath('sd-panel')
    j = []
    for i, p in enumerate(panels):
        caption = inner_text(p)
        tags = p.xpath('sd-tag')
        j_tags = []
        for t in tags:
            j_tags.append({
                'text': t.text,
                'category': t.get('category', ''),
                'type': t.get('type', ''),
                'role': t.get('role', ''),
                'category_score': t.get('category_score', ''),
                'type_score': t.get('type_score', ''),
                'role_score': t.get('role_score', ''),
            })
        j.append({
            'caption': caption,
            'label': str(i),
            'tags': j_tags
        })
    return j


class SDCollection(BaseCollection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SDArticle(BaseArticle):
    def __init__(self, data):
        super().__init__(data)
        self.pub_date = self.get('pub_date', '')
        self.update_properties({'pub_date': self.pub_date})
        self.children = range(self.nb_figures)


class SDFigure(BaseFigure):
    def __init__(self, data):
        super().__init__(data)
        if self.caption:
            self.formatted_caption = tag_it(self.caption, format='xml')
            self.update_properties({'formatted_caption': self.formatted_caption})
            panels = xml2json(self.formatted_caption)
            self.children = panels
        # self.children = [SDPanel(self)]  # provisional until we fix automatic panelization in general case


class SDPanel(BasePanel):
    def __init__(self, data):
        super().__init__(data)
        self.tags = self.get('tags', '')
        self.children = [SDTag(t) for t in self.tags]


class SDTag(BaseTag):
    def __init__(self, data):
        super().__init__(data)
        self.category_score = self.get('category_score', '')
        self.type_score = self.get('type_score', '')
        self.role_score = self.get('role_score', '')
        self.update_properties({
            'category_score': self.category_score,
            'type_score': self.type_score,
            'role_score': self.role_score,
        })


class EEBAPI(API):

    GET_COLLECTION = "collection/"
    GET_ARTICLE = "doi/"
    GET_FIGURE = "figure"

    def collection(self, collection_name):
        url = EEB_PUBLIC_API + self.GET_COLLECTION + collection_name
        data = self.rest2data(url)
        article_list = SDCollection(data, collection_name)
        return article_list

    def article(self, doi):
        url = EEB_PUBLIC_API + self.GET_ARTICLE + doi
        data = self.rest2data(url)
        if data:
            article = SDArticle(data)  # most recent version should be first item in list
        else:
            article = None
        return article

    def figure(self, figure_index=0, doi=''):
        params = {'doi': doi, 'position_idx': figure_index}
        url = EEB_PUBLIC_API + self.GET_FIGURE
        data = self.rest2data(url, params)
        if data:
            figure = SDFigure(data)
        else:
            figure = None
        return figure

    def panel(self, data):
        panel = SDPanel(data)
        return panel

    def tag(self, data):
        if data:
            tag = SDTag(data)
        else:
            tag = None
        return tag


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
