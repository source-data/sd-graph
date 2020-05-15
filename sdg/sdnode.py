import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Dict


class SDNode:

    def __init__(self, data: Dict):
        self._data = data
        if isinstance(self._data, list):
            self._data = self._data[0]
        self.properties = {'source': 'sdneo'}
        self.label = self.__class__.__name__
        self.children = []

    def add_properties(self, prop: Dict):
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

    def collection(self, collection_name):
        raise NotImplementedError

    def article(self, doi):
        raise NotImplementedError

    def figure(self, doi, figure_index=1):
        raise NotImplementedError

    def panel(self, id):
        raise NotImplementedError

    def tag(self, data):
        raise NotImplementedError
