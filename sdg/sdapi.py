import argparse
import requests
import re
from typing import List
import common.logging
from .sdnode import (
    API,
    BaseCollection, BaseArticle, BaseFigure, BasePanel, BaseTag
)
from . import SD_API_URL, SD_API_USERNAME, SD_API_PASSWORD


class SDCollection(BaseCollection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_properties({'source': 'sdapi'})


class SDArticle(BaseArticle):
    def __init__(self, data):
        super().__init__(data)
        self.year = self.get('year', '')
        self.pmid = self.get('pmid', '')
        self.import_id = self.get('pmcid', '')
        self.nb_figures = int(self.get('nbFigures', 0)) # SD API uses this...
        self.update_properties({
            'pmid': self.pmid,
            'import_id': self.import_id,
            'year': self.year,  # unfortunately SD has no pub_date properties
            'nb_figures': self.nb_figures,
            'source': 'sdapi',
        })
        self.children = range(1, self.nb_figures+1)


class SDFigure(BaseFigure):
    def __init__(self, data):
        super().__init__(data)
        self.fig_label = self.get('label', '')  # and not fig_label as in JATS
        self.update_properties({
            'fig_label': self.fig_label,
            'source': 'sdapi',
        })


class SDPanel(BasePanel):
    def __init__(self, data):
        self.panel_id = data.get('current_panel_id', '')
        # the SD API panel method includes 'reverse' info on source paper, figures, and all the other panels
        # take the portion of the data returned by the REST API that concerns panels
        figure = data.get('figure', '')
        if figure:
            panels = figure.get('panels', [])
        else:
            panels = []
        # find current panel which is provided in a list and not in a dictionary :-(
        panel_data = [p for p in panels if p['panel_id']==self.panel_id]
        if panel_data:
            panel_data = panel_data[0]
        else:
            panel_data = {}
        # call parent constructor with relevant data
        super().__init__(panel_data)
        # override paper_doi using paper info
        paper_info = data.get('paper', {})
        self.paper_doi = paper_info.get('doi', '')
        # we keep the figure label as well
        figure_info = data.get('figure', {})
        self.fig_label = figure_info.get('label', '')
        # find this panel's id using current_panel_id
        self.formatted_caption = self._data.get('formatted_caption', '')
        coords = self._data.get('coords', {})
        self.coords = ', '.join([f'{k}={v}' for k, v in coords.items()])
        self.tags = self._data.get('tags', [])
        self.update_properties({
            'paper_doi': self.paper_doi,
            'fig_label': self.fig_label,
            'panel_id': self.panel_id,
            'formatted_caption': self.formatted_caption, 
            'coords': self.coords,
            'source': 'sdapi',
        })
        self.children = self.rm_empty(self.tags)


class SDTag(BaseTag):
    def __init__(self, data):
        super().__init__(data)
        self.ext_ids = '///'.join(self._data.get('external_ids', []))
        self.ext_dbs = '///'.join(self._data.get('external_databases', []))
        self.in_caption = self._data.get('in_caption', '') == 'Y'
        self.ext_names = '///'.join(self._data.get('external_names', []))
        self.ext_tax_ids = '///'.join(self._data.get('external_tax_ids', []))
        self.ext_tax_names = '///'.join(self._data.get('external_tax_names', []))
        self.ext_urls = '///'.join(self._data.get('external_urls', []))
        self.update_properties({
            'ext_ids': self.ext_ids,
            'ext_dbs': self.ext_dbs,
            'in_caption': self.in_caption,
            'ext_names': self.ext_names,
            'ext_tax_ids': self.ext_tax_ids,
            'ext_tax_names': self.ext_tax_names,
            'ext_urls': self.ext_urls,
            'source': 'sdapi',
        })


class SDAPI(API):

    GET_COLLECTION = 'collection/'
    GET_LIST = 'papers'
    GET_ARTICLE = 'paper/'
    GET_FIGURE = 'figure/'
    GET_PANEL = 'panel/'

    def __init__(self):
        super().__init__()
        authenticated_session = requests.Session()
        authenticated_session.auth = (SD_API_USERNAME, SD_API_PASSWORD)
        self.session_retry = self.requests_retry_session(session=authenticated_session)
        self.collection_id = None

    def collection(self, collection_names: List[str]) -> SDCollection:
        def get_collection_id(collection_name: str):
            url = SD_API_URL + self.GET_COLLECTION + collection_name
            data = self.rest2data(url)
            collection_id = data[0]['collection_id']
            return collection_id

        self.collection_id = get_collection_id(collection_names[0])
        url = SD_API_URL + self.GET_COLLECTION + self.collection_id + "/" + self.GET_LIST
        data = self.rest2data(url)
        collection = SDCollection({collection_names[0]: data}, [self.collection_id])
        return collection

    def article(self, doi):
        url = SD_API_URL + self.GET_COLLECTION + self.collection_id + "/" + self.GET_ARTICLE + doi
        article = self.generate_sdnode(url, SDArticle)
        return article

    def figure(self, figure_index=1, doi=''):
        url = SD_API_URL + self.GET_COLLECTION + self.collection_id + "/" + self.GET_ARTICLE + doi + "/" + self.GET_FIGURE + str(figure_index)
        figure = self.generate_sdnode(url, SDFigure)
        return figure

    def panel(self, id):
        url = SD_API_URL + self.GET_PANEL + id
        panel = self.generate_sdnode(url, SDPanel)
        return panel

    def tag(self, data):
        # because tags are only accessible through a panel, there is no request to the SD_API_URL
        # the data is provided directly and obtained from prior request with panel(panel_id).children
        tag = SDTag(data)
        return tag


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = argparse.ArgumentParser( description="interace to the SourceData API" )
    parser.add_argument('collection', nargs="?", default="PUBLICSEARCH", help="Takes the name of a collection (try \"PUBLICSEARCH\") nd returns the list of papers")
    parser.add_argument('-L', '--listing', action="store_true", help="List of articles in the collection.") 
    parser.add_argument('-D', '--doi', default='', help="Takes a doi and return article information")
    parser.add_argument('-F', '--figure', default='', help="Takes the figure index and returns the figure legend for the figure in the paper specified with the --doi option") 
    parser.add_argument('-P', '--panel', default='', help="Takes the id of a panel and returns the tagged text of the legend")
    args = parser.parse_args()
    collection_name = args.collection
    listing = args.listing
    doi = args.doi
    fig = args.figure
    panel_id = args.panel
    sdapi = SDAPI()
    if collection_name:
        collection = sdapi.collection([collection_name])
        print(f'collection {collection.name} has id = {collection.id} and has {len(collection)} articles.')

    if listing:
        for doi in collection.children:
            a = sdapi.article(doi)
            print(f"{a.doi}\t{a.import_id}\t{a.title}")

    if doi:
        article = sdapi.article(doi)
        print('doi:', article.doi)
        print('title:', article.title)
        print('journal:', article.journal)
        print('year:', article.year)
        print('pmid:', article.pmid)
        print('number of figures:', article.nb_figures)

    if fig and doi:
        figure = sdapi.figure(fig, doi)
        print('label:', figure.label)
        print('caption:', figure.caption)
        print('url:', figure.href)
        print('panel ids:', '\t'.join(figure.children))

    if panel_id:
        panel = sdapi.panel(panel_id)
        print('label:', panel.label)
        print('url:', panel.href)
        print('caption:', panel.caption)
        print()
        print('formatted caption:', panel.formatted_caption)
        print('coordinates:', panel.coords)
        for tag_data in panel.children:
           print(sdapi.tag(tag_data))
