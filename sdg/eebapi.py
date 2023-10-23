import argparse
import json
from lxml.etree import fromstring
import common.logging
from neotools.utils import inner_text, cleanup
from .sdnode import (
    API,
    BaseCollection, BaseArticle, BaseFigure, BasePanel, BaseTag
)
from smtag.pipeline import SmartTagger
from . import EEB_INTERNAL_API
from typing import Dict

logger = common.logging.get_logger(__name__)

TAGGING_ENGINE = SmartTagger()

def tag_and_panelize(text: str):
    text = cleanup(text)
    tagging_result_json = TAGGING_ENGINE(text)
    tagging_result = json.loads(tagging_result_json)
    tagged_panels = smtag2json(tagging_result)
    return tagged_panels


def get_score(t, score_name, default):
    try:
        score = t.get(score_name)
    except:
        return default
    try:
        score_as_percent = int(score * 100)
    except:
        return default
    return str(score_as_percent)

AttrConversion = {
    "CELL": "cell",
    "GENEPROD": "geneprod",
    "SMALL_MOLECULE": "small_molecule",
    "SUBCELLULAR": "subcellular",
    "ORGANISM": "organism",
    "TISSUE": "tissue",
    "MEASURED_VAR": "assayed",
    "CONTROLLED_VAR": "intervention",
}
def get_entity_attribute(entity, attr_name, default):
    attr_value = entity.get(attr_name, None)
    # attr_name can be absent from entity, or it can contain an empty string. We're not interested in either.
    if attr_value is None:
        return default
    return AttrConversion.get(attr_value, attr_value)

def smtag2json(panels):
    j = []
    for i, panel in enumerate(panels):
        j_tags = []
        for t in panel["entities"]:
            j_tags.append({
                'text': t.get('text'),
                'start': t.get('start'),
                'end': t.get('end'),
                'category': get_entity_attribute(t, 'category', ''),
                'type': get_entity_attribute(t, 'type', ''),
                'role': get_entity_attribute(t, 'role', ''),
                'category_score': get_score(t, 'category_score', ''),
                'type_score': get_score(t, 'type_score', ''),
                'role_score': get_score(t, 'role_score', ''),
            })
        j.append({
            'caption': panel.get('text', ''),
            'label': str(i),
            'tags': j_tags
        })
    return j


class SDCollection(BaseCollection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_properties({'source': 'eebapi'})


class SDArticle(BaseArticle):
    def __init__(self, data):
        super().__init__(data)
        self.update_properties({
            'source': 'eebapi',
        })
        self.children = range(self.nb_figures)


class SDFigure(BaseFigure):
    def __init__(self, data):
        super().__init__(data)
        if self.caption:
            self.update_properties({
                'source': 'eebapi',
            })
            panels = tag_and_panelize(self.caption)
            self.children = panels
        # self.children = [SDPanel(self)]  # provisional until we fix automatic panelization in general case


class SDPanel(BasePanel):
    def __init__(self, data):
        super().__init__(data)
        self.update_properties({'source': 'eebapi'})
        self.tags = self.get('tags', '')
        self.children = [SDTag(t) for t in self.tags]


class SDTag(BaseTag):
    def __init__(self, data: Dict):
        super().__init__(data)
        self.category_score = self.get('category_score', '')
        self.type_score = self.get('type_score', '')
        self.role_score = self.get('role_score', '')
        self.update_properties({
            'category_score': self.category_score,
            'type_score': self.type_score,
            'role_score': self.role_score,
            'source': 'eebapi',
        })


class EEBAPI(API):

    GET_COLLECTION = 'collection/'
    GET_ARTICLE = 'doi/'
    GET_FIGURE = 'figure'

    def collection(self, collection_names):
        data = {}
        for name in collection_names:
            url = EEB_INTERNAL_API + self.GET_COLLECTION + name
            data[name] = self.rest2data(url)
        collection = SDCollection(data)
        return collection

    def article(self, doi):
        url = EEB_INTERNAL_API + self.GET_ARTICLE + doi
        data = self.rest2data(url)
        if data:
            article = SDArticle(data)  # most recent version should be first item in list
        else:
            article = None
        return article

    def figure(self, figure_index=0, doi=''):
        params = {'doi': doi, 'position_idx': figure_index}
        url = EEB_INTERNAL_API + self.GET_FIGURE
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
    common.logging.configure_logging()
    parser = argparse.ArgumentParser(description='interace to the SourceData API' )
    parser.add_argument('-L', '--listing', action='store_true', help='List of articles in the collection.') 
    parser.add_argument('-D', '--doi', default='', help='Takes a doi and return article information')
    parser.add_argument('-F', '--figure', default='', help='Takes the figure index and returns the figure legend for the figure in the paper specified with the --doi option') 
    parser.add_argument('-C', '--collections', nargs="+", help='The collection that forms the base of the Early Evidence Base.') 

    args = parser.parse_args()
    listing = args.listing
    doi_arg = args.doi
    fig = args.figure
    collection_names = args.collections
    eebapi = EEBAPI()

    collections = eebapi.collection(collection_names)
    logger.info(f'Collection {[c.name for c in collections]} have {[len(c) for c in collections]} articles.')

    if listing:
        for coll in collections:
            for doi in coll.children:
                a = eebapi.article(doi)
                logger.info(f'{doi}: {a.title}')

    if doi_arg:
        article = eebapi.article(doi_arg)
        logger.info('doi: %s', article.doi)
        logger.info('title: %s', article.title)
        logger.info('journal: %s', article.journal)
        logger.info('number of figures: %s', article.nb_figures)

    if fig and doi_arg:
        figure = eebapi.figure(fig, doi_arg)
        logger.info('label: %s', figure.fig_label)
        logger.info('caption: %s', figure.caption)
        for panel in figure.children:
            logger.info(f'pseudo panel {panel.panel_id}')
            logger.info('formatted tagged caption: %s', panel.formatted_caption)
            for t in panel.children:
                sd_tag = SDTag(t)
                logger.info(sd_tag.properties)
