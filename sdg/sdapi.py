import requests
import argparse
from . import SD_API_URL, SD_API_USERNAME, SD_API_PASSWORD

GET_COLLECTION = "collection/"
GET_LIST = "papers"
GET_ARTICLE = "paper/"
GET_FIGURE = "figure/"
GET_PANEL = "panel/"


def rest2data(url, usr=SD_API_USERNAME, pswd=SD_API_PASSWORD):
    data = dict()
    try:
        response = requests.get(url, auth=(usr, pswd))
        try: 
            data = response.json()
        except Exception as e:
            print("WARNING: problem with loading json object with %s" % url)
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
        if self._data is not None:
            self.properties = {}
            self.label = self.__class__.__name__
            self.children = {}
        else:
            self = None

    @staticmethod
    def rm_empty(list):
        return [e for e in list if e]

    def __str__(self):
        return "; ".join([f"{k}: {v}" for k, v in  self._data.items()])


class SDArticle(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.title = self._data.get('title', '')
        self.journal = self._data.get('journal', '')
        self.year = self._data.get('year', '')
        self.doi = self._data.get('doi', '')
        self.pmid = self._data.get('pmid' '')
        self.import_id = self._data.get('pmcid', '')
        self.nb_figures = int(self._data.get('nbFigures', 0))
        self.properties = {
            'doi': self.doi,
            'pmid': self.pmid,
            'import_id': self.import_id,
            'title': self.title,
            'journalName': self.journal,
            'year': self.year,
            'nb_figures': self.nb_figures
        }
        self.children = range(1, self.nb_figures+1)


class SDFigure(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.fig_label = self._data.get('label', '')
        self.caption = self._data.get('caption', '')
        self.href = self._data.get('href', '')
        panels = self._data.get('panels', [])
        self.properties = {
            'fig_label': self.fig_label,
            'caption': self.caption,
            'href': self.href,
        }
        self.children = self.rm_empty(panels)


class SDPanel(SDNode):
    def __init__(self, data):
        # the SD API panel method includes 'reverse' info on source paper, figures, and all the other panels
        # we keep the paper doi and figure label
        paper_info = data.get('paper', {})
        self.paper_doi = paper_info.get('doi', '')
        # we keep the figure label as well
        figure_info = data.get('figure', '')
        self.fig_label = figure_info.get('lable', '')
        # find this panel's id using current_panel_id
        self.panel_id = data['current_panel_id']
        # take the portion of the data returned by the REST API that concerns panels
        panels = data['figure']['panels']
        # find current panel which is provided in a list and not in a dictionary :-(
        data = [p for p in panels if p['panel_id']==self.panel_id][0]
        # call parent constructor with relevant data
        super().__init__(data)
        self.href = self._data.get('href', '')
        self.panel_label = self._data.get('label', '')
        self.caption = self._data.get('caption', '')
        self.formatted_caption = self._data.get('formatted_caption', '')
        coords = self._data.get('coords', {})
        self.coords = ", ".join([f"{k}={v}" for k, v in coords.items()])
        tags = self._data.get('tags', [])
        self.properties = {
            "paper_doi": self.paper_doi,
            "fig_label": self.fig_label,
            "panel_id": self.panel_id,
            "panel_label": self.panel_label,
            "caption": self.caption, 
            "formatted_caption": self.formatted_caption, 
            "coords": self.coords, 
            "href": self.href
        }
        self.children = self.rm_empty(tags)


class SDTag(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.tag_id = self._data.get('id', '')
        category = self._data.get('category', None)
        if category == '': # SD API returns category with an empty string for entities...
            self.category = 'entity'
        elif category is None:
            self.category = ''
        else:
            self.category = category
        self.type = self._data.get('type', '')
        self.role = self._data.get('role', '')
        self.text = self._data.get('text', '')
        self.ext_ids = "///".join(self._data.get('external_ids', []))
        self.ext_dbs = "///".join(self._data.get('external_databases', [])) 
        self.in_caption = self._data.get('in_caption', '') == "Y" 
        self.ext_names = "///".join(self._data.get('external_names', []))
        self.ext_tax_ids = "///".join(self._data.get('external_tax_ids', []))   
        self.ext_tax_names = "///".join(self._data.get('external_tax_names', []))
        self.ext_urls = "///".join(self._data.get('external_urls', []))
        self.properties = {
            'tag_id': self.tag_id,
            'category': self.category, 
            'type': self.type, 
            'role': self.role, 
            'text': self.text, 
            'ext_ids': self.ext_ids, 
            'ext_dbs': self.ext_dbs, 
            'in_caption': self.in_caption, 
            'ext_names': self.ext_names, 
            'ext_tax_ids': self.ext_tax_ids,
            'ext_tax_names': self.ext_tax_names, 
            'ext_urls': self.ext_urls,
        }


class ArticleList:

    def __init__(self, data):
        self.doi_list = [a.get('doi', '') for a in data]
        self.title_list = [a.get('title', '') for a in data]
        self.title_doi_dictionary = {a['id']: {"title": a['title'], "doi": a['doi']} for a in data}


class SDAPI:

    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection_id = self.get_collection_id(self.collection_name)
        self.doi_list = self.article_list().doi_list
        self.N = len(self.doi_list)
        print(f"collection {self.collection_id } contains {self.N} papers.")

    def get_collection_id(self, collection_name):
        url = SD_API_URL + GET_COLLECTION + collection_name
        data = rest2data(url)
        collection_id = data[0]['collection_id']
        return collection_id

    def article_list(self):
        url = SD_API_URL + GET_COLLECTION + self.collection_id + "/" + GET_LIST
        data = rest2data(url)
        article_list = ArticleList(data)
        return article_list

    def article(self, doi):
        url = SD_API_URL + GET_COLLECTION + self.collection_id + "/" + GET_ARTICLE + doi
        data = rest2data(url)
        article = SDArticle(data)
        return article

    def figure(self, doi, figure_index=1):
        url = SD_API_URL + GET_COLLECTION + self.collection_id + "/" + GET_ARTICLE + doi + "/" + GET_FIGURE + str(figure_index)
        data = rest2data(url)
        figure = SDFigure(data)
        return figure

    def panel(self, id):
        url = SD_API_URL + GET_PANEL + id
        data = rest2data(url)
        panel = SDPanel(data)
        return panel

    def tag(self, data):
        # because tags are only accessible through a panel, there is no request to the SD_API_URL
        # the data is provided directly and obtained from prior request with panel(panel_id).children
        tag = SDTag(data)
        return tag

    def __len__(self):
        return self.N


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description="interace to the SourceData API" )
    parser.add_argument('collection', nargs="?", default="PUBLICSEARCH", help="Takes the name of a collection (try \"PUBLICSEARCH\") nd returns the list of papers")
    parser.add_argument('-L', '--listing', action="store_true", help="List of articles in the collection.") 
    parser.add_argument('-D', '--doi', default = '', help="Takes a doi and return article information")
    parser.add_argument('-F', '--figure', default = '', help="Takes the figure index and returns the figure legend for the figure in the paper specified with the --doi option") 
    parser.add_argument('-P', '--panel', default='', help="Takes the id of a panel and returns the tagged text of the legend")
    args = parser.parse_args()
    collection_name = args.collection
    listing = args.listing
    doi = args.doi
    fig = args.figure
    panel_id = args.panel
    sdapi = SDAPI(collection_name)
    if collection_name:
        collection_id = sdapi.collection_id
        print(f"collection {sdapi.collection_name} has id = {collection_id} and has {len(sdapi)} articles.")

    if listing:
        article_list = sdapi.article_list()
        for doi in article_list.doi_list:
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
        figure = sdapi.figure(doi, fig)
        print("label:", figure.label)
        print("caption:", figure.caption)
        print("url:", figure.href)
        print("panel ids:", "\t".join(figure.children))

    if panel_id:
        panel = sdapi.panel(panel_id)
        print("label:", panel.label)
        print("url:", panel.href)
        print("caption:", panel.caption)
        print()
        print("formatted caption:", panel.formatted_caption)
        print("coordinates:", panel.coords)
        for tag_data in panel.children:
           print(sdapi.tag(tag_data))