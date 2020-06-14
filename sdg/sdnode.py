import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Dict
from . import logger


class SDNode:

    def __init__(self, data: Dict):
        self._data = data
        if isinstance(self._data, list) and self._data:
            self._data = self._data[0]
        self.properties = {}
        self.label = self.__class__.__name__
        self.children = []

    def update_properties(self, prop: Dict):
        self.properties = {**self.properties, **prop}

    @staticmethod
    def rm_empty(list):
        return [e for e in list if e]

    def get(self, key, default):
        # should never return None, but rather returns default value if value from self._data is None or [] or False
        val = self._data.get(key, default)
        if not val:
            val = default
        return val

    def __str__(self):
        return "; ".join([f"{k}: {v}" for k, v in  self._data.items()])


class BaseCollection(SDNode):
    def __init__(self, data, name, id=None):
        super().__init__(data)
        self.name = name
        self.id = id or ''
        self.update_properties({'name': name, 'id': id})
        children = []
        for d in data:
            doi = d.get('doi', '')
            sdid = d.get('id', '')
            title = d.get('title', '')
            if doi: # check if alreeady there!
                children.append(doi)
            elif sdid:
                logger.warning(f"using sdid {sdid} instead of doi for: \n{title}.")
                children.append(sdid)
            else:
                logger.error(f"no doi and no sd id for {title} in collection {name}.")
        self.children = children

    def __len__(self):
        return len(self.children)


class BaseArticle(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.get('title', '')
        self.journal = self.get('journal', '')
        self.doi = self.get('doi', '')
        self.nb_figures = int(self.get('nb_figures', 0))
        self.update_properties({
            'doi': self.doi,
            'title': self.title,
            'journalName': self.journal,
            'nb_figures': self.nb_figures
        })
        self.children = range(self.nb_figures)


class BaseFigure(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.paper_doi = self.get('doi', '')
        self.fig_label = self.get('fig_label', '')
        self.fig_title = self.get('fig_title', '')
        self.caption = self.get('caption', '')
        self.href = self._data.get('href', '') # href_graphics?
        self.panels = self._data.get('panels', [])
        self.update_properties({
            'fig_title': self.fig_title,
            'fig_label': self.fig_label,
            'caption': self.caption,
            'href': self.href,
        })
        self.children = self.rm_empty(self.panels)


class BasePanel(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.paper_doi = self.get('doi', '')
        self.panel_label = self.get('label', '')
        self.caption = self.get('caption', '')
        self.href = self.get('href', '')
        self.update_properties({
            'paper_doi': self.paper_doi,
            'panel_label': self.panel_label,
            'caption': self.caption,
            'href': self.href
        })
        self.children = []


class BaseTag(SDNode):
    def __init__(self, data):
        super().__init__(data)
        self.tag_id = self._data.get('id', '')
        self.category = self.get('category', 'entity')
        self.type = self._data.get('type', '')
        self.role = self._data.get('role', '')
        self.text = self._data.get('text', '')
        self.update_properties({
            'tag_id': self.tag_id,
            'category': self.category,
            'type': self.type,
            'role': self.role,
            'text': self.text
        })


class API:

    def __init__(self):
        self.session_retry = self.requests_retry_session()

    @staticmethod
    def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):
        # from  https://www.peterbe.com/plog/best-practice-with-retries-with-requests
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def rest2data(self, url: str, params: Dict = None) -> Dict:
        data = dict()
        try:
            response = self.session_retry.get(url, params=params, timeout=30)
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
            if data:
                return data
            else:
                print(f"response to {url} is empty")
                return dict()

    def generate_sdnode(self, url, Cls, *args, **kwargs) -> SDNode:
        data = self.rest2data(url)
        sdnode = Cls(data, *args, **kwargs)
        return sdnode

    def collection(self, collection_name) -> BaseCollection:
        raise NotImplementedError

    def article(self, doi) -> BaseArticle:
        raise NotImplementedError

    def figure(self, doi, figure_index=1) -> BaseFigure:
        raise NotImplementedError

    def panel(self, id) -> BasePanel:
        raise NotImplementedError

    def tag(self, data) -> BaseTag:
        raise NotImplementedError
