import requests
import argparse
import json
from smtag.predict.cartridges import CARTRIDGE
from smtag.predict.engine import SmtagEngine
from . import EEB_PUBLIC_API

GET_LIST = "papers"
GET_COVID19 = "covid19"
GET_ARTICLE = "doi/"
GET_FIGURE = "figure"


TAGGING_ENGINE = SmtagEngine(CARTRIDGE)


def tag(text, format):
    tags = TAGGING_ENGINE.tag(text, 'sd-tag', format)
    if format == 'json':
        tags = json.loads(tags[0])
        tags = tags['smtag'][0]['entities']
    return tags


def rest2data(url, params=None):
    data = dict()
    try:
        response = requests.get(url, params)
        try:
            data = response.json()
        except Exception as e:
            print(f"WARNING: problem with loading json object with {url}")
            print(type(e), e)
            print(response.json())
    except Exception as e:
        print("failed to get response from server")
        print(type(e), e)
    finally:
        if data is not None:
            return data
        else:
            print("response is empty")
            return dict()


class SDNode:

    def __init__(self, data):
        self._data = data
        if isinstance(self._data, list):
            self._data = self._data[0]
        self.properties = {}
        self.label = self.__class__.__name__
        self.children = {}

    @staticmethod
    def rm_empty(list):
        return [e for e in list if e]

    def get(self, key, default):
        return self._data.get(key, default)

    def __str__(self):
        return "; ".join([f"{k}: {v}" for k, v in  self._data.items()])


class SDArticle(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.get('title', '')
        self.journal = self.get('journal', '')
        self.doi = self.get('doi', '')
        self.nb_figures = int(self.get('nb_figures', 0))  # remember to change this in sdg!
        self.properties = {
            'doi': self.doi,
            'title': self.title,
            'journalName': self.journal,
            'nb_figures': self.nb_figures
        }
        self.children = range(self.nb_figures)


class SDFigure(SDNode):
    def __init__(self, data):
        super().__init__(data)
        try:
            self.paper_doi = self.get('doi', '')
        except AttributeError:
            import pdb; pdb.set_trace()
        self.fig_label = self.get('fig_label', '')
        self.fig_title = self.get('fig_title', '')
        self.caption = self.get('caption', '')
        self.properties = {
            'fig_label': self.fig_label,
            'title': self.fig_title,
            'caption': self.caption,
        }
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
            self.formatted_caption = tag(fig.caption, format='xml')
        else:
            self.formatted_caption = ''
        self.properties = {
            "paper_doi": self.paper_doi,
            "fig_label": self.fig_label,
            "panel_id": self.panel_id,
            "panel_label": self.panel_label,
            "caption": self.caption, 
            "formatted_caption": self.formatted_caption
        }
        if self.caption:
            self.children = tag(self.caption, format='json')
        else:
            self.children = []


class SDTag(SDNode):
    def __init__(self, data):
        super().__init__(data)
        # {'category': 'assay', 'category_score': '57', 'text': 'histopathology'}, 
        # {'type': 'tissue', 'type_score': '52', 'text': 'lungs'}
        # {'type': 'geneprod', 'role': 'intervention', 'type_score': '39', 'role_score': '74', 'text': 'ACE2'}
        category = self.get('category', None)
        if category is None: # SD API returns category with an empty string for entities...
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
        self.properties = {
            'category': self.category, 
            'category_score': self.category_score,
            'type': self.type, 
            'type_score': self.type_score,
            'role': self.role, 
            'role_score': self.role_score,
            'text': self.text,
        }


class ArticleList:

    def __init__(self, data):
        self.doi_list = [a.get('doi', '') for a in data]
        self.title_list = [a.get('title', '') for a in data]
        self.title_doi_dictionary = {a['doi']: {"title": a['title'], "doi": a['doi']} for a in data}


class EEBAPI:

    def __init__(self):
        self.doi_list = self.article_list().doi_list
        self.N = len(self.doi_list)
        print(f"COVID-19 has {self.N} papers.")

    def article_list(self):
        url = EEB_PUBLIC_API + GET_COVID19
        data = rest2data(url)
        article_list = ArticleList(data)
        return article_list

    def article(self, doi):
        url = EEB_PUBLIC_API + GET_ARTICLE + doi
        data = rest2data(url)
        if data:
            article = SDArticle(data)  # most recent version should be first item in list
        else:
            article = None
        return article

    def figure(self, doi, figure_index=1):
        params = {'doi': doi, 'position_idx': figure_index}
        url = EEB_PUBLIC_API + GET_FIGURE
        data = rest2data(url, params)
        if data:
            figure = SDFigure(data)  # most recent version should be first item in list
        else:
            figure = None
        return figure

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
    eebapi = EEBAPI()

    if listing:
        article_list = eebapi.article_list()
        for doi in article_list.title_doi_dictionary:
            print(f"{doi}: {article_list.title_doi_dictionary[doi]}")

    if doi_arg:
        article = eebapi.article(doi_arg)
        print('doi:', article.doi)
        print('title:', article.title)
        print('journal:', article.journal)
        print('number of figures:', article.nb_figures)

    if fig and doi_arg:
        figure = eebapi.figure(doi_arg, fig)
        print("label:", figure.label)
        print("caption:", figure.caption)
        print("tagged", figure.children)
        for panel in figure.children:
            print(f"pseudo panel {panel.panel_id}")
            for t in panel.children['smtag'][0]['entities']:
                sd_tag = SDTag(t)
                print(sd_tag.properties)
