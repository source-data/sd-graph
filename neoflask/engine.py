from typing import Dict
from neotools.db import Instance, Query
from .queries import (
    STATS, BY_DOI, FIG_BY_DOI_IDX, PANEL_BY_NEO_ID,
    REVIEW_PROCESS_BY_DOI, BY_REVIEWING_SERVICE,
    BY_AUTO_TOPICS, AUTOMAGIC,
    LUCENE_SEARCH, SEARCH_DOI,
    COVID19, REFEREED_PREPRINTS,
    COLLECTION_NAMES, SUBJECT_COLLECTIONS,
)


def param_from_request(request, query: Query) -> Dict:
    """
    Take a request and extract the values of the parameters that are required for parameter substitution in the Query.

    The dictionary query.map maps the substitution variable of the query to the parameters provided in the request.
    The names of the substitutions variables in the query are the keys of the dictionary query.map
    The code of the query is provided in query.code and will be checked to make sure it includes the substitution variables listed in query.map.
    The value of query.map[key] is a list. The first element of this list is the name of the parameter expected in the request.
    The value of the parameter will then be substituted in the code of the query.
    The second second element of the list is the default value of this parameter if no value was provided in the request.
    If query.map[key] is the empty list, it means that request itself is a string and is the value that needs to be substituted.

    Arguments:
        request (str or ...): the request received by the flask App from which parameters value needs to be extracted
        query (Query): the database query that will be used

    Returns:
        (Dict): a dictionary with the values of each substitution variable needed by the query
    """

    params_dict = {}
    for query_var, request_param in query.map.items():
        if request_param:
            params_dict[query_var] = request.args.get(request_param[0], request_param[1])  # the value of the request param is mapped to the Query substituion variable
        else:
            assert isinstance(request, str), f"request was not a string ({request})."
            params_dict[query_var] = request  # the request is a string and is the content of the Query variable
    return params_dict


class Engine:
    """
    Handle requests received from the Flask app, make respective database queries and returns the results.

    Arguments:
        neo4j_db (Instance): a neotools.db.Instance that connects to the database and handles transactions
    """
    def __init__(self, neo4j_db: Instance):
        self.neo4j_db = neo4j_db

    def ask_neo(self, query: Query) -> Dict:
        """
        Run a query and return the database results as dictionary with the keys specified in the query.returns list.
        """
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            data = [r.data(*query.returns) for r in results]  # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html
            return data
        data = self.neo4j_db.query_with_tx_funct(tx_funct, query)
        return data

    def stats(self, request) -> Dict:
        query = STATS()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)

    def by_reviewing_service(self, limit_date: str) -> Dict:
        query = BY_REVIEWING_SERVICE()
        query.params = param_from_request(limit_date, query)
        return self.ask_neo(query)

    def by_doi(self, doi: str) -> Dict:
        query = BY_DOI()
        query.params = param_from_request(doi, query)
        return self.ask_neo(query)

    def review_by_doi(self, doi: str) -> Dict:
        query = REVIEW_PROCESS_BY_DOI()
        query.params = param_from_request(doi, query)
        return self.ask_neo(query)

    def fig_by_doi_idx(self, request) -> Dict:
        query = FIG_BY_DOI_IDX()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)

    def panel_by_neo_id(self, id: str) -> Dict:
        query = PANEL_BY_NEO_ID()
        query.params = param_from_request(id, query)
        return self.ask_neo(query)

    def by_auto_topics(self, limit_date: str) -> Dict:
        query = BY_AUTO_TOPICS()
        query.params = param_from_request(limit_date, query)
        return self.ask_neo(query)

    def automagic(self, limit_date: str) -> Dict:
        query = AUTOMAGIC()
        query.params = param_from_request(limit_date, query)
        return self.ask_neo(query)

    def search(self, query: str) -> Dict:
        query_lucene = LUCENE_SEARCH()
        query_lucene.params = param_from_request(query, query_lucene)
        response_lucene = self.ask_neo(query_lucene)

        query_doi = SEARCH_DOI()
        query_doi.params = param_from_request(query, query_doi)
        found_doi = self.ask_neo(query_doi)
        if found_doi:
            response = found_doi
        else:
            response = response_lucene
        return response

    def covid19(self, request) -> Dict:
        query = COVID19()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)

    def refereed_preprints(self, request) -> Dict:
        query = REFEREED_PREPRINTS()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)

    def subjects(self, request) -> Dict:
        query = COLLECTION_NAMES()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)

    def subject_collection(self, request) -> Dict:
        query = SUBJECT_COLLECTIONS()
        query.params = param_from_request(request, query)
        return self.ask_neo(query)
