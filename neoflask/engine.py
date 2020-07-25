import json
import re
from typing import Dict, NewType
from neotools.db import Instance, Query
from .queries import (
    STATS, BY_DOI, FIG_BY_DOI_IDX, PANEL_BY_NEO_ID,
    REVIEW_PROCESS_BY_DOI, BY_REVIEWING_SERVICE,
    BY_HYP, AUTOMAGIC,
    BY_METHOD, PANEL_SUMMARY,
    LUCENE_SEARCH, SEARCH_DOI,
    COVID19, REFEREED_PREPRINTS,
)

# symbolic type for a json string
json_str = NewType('json_str', str)


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
        Run a query a nd
        """
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            data = [r.data(*query.returns) for r in results]  # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html
            return data
        data = self.neo4j_db.query_with_tx_funct(tx_funct, query)
        return data

    def query2json(self, query: Query) -> json_str:
        """
        Take a Query, run it through the database and returns the results as json string

        Arguments:
            query (Query): the query to be run

        Returns:
            (json_str): the stringified json results returned by the database
        """
        data = self.ask_neo(query)
        return json.dumps(data, indent=2)

    def stats(self, request):
        query = STATS()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    # def by_molecule(self, request):
    #     query = BY_MOLECULE()
    #     query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
    #     return self.query2json(query)

    def by_method(self, request):
        query = BY_METHOD()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def by_reviewing_service(self, limit_date):
        query = BY_REVIEWING_SERVICE()
        query.params = param_from_request(limit_date, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def by_doi(self, doi):
        query = BY_DOI()
        query.params = param_from_request(doi, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def review_by_doi(self, doi):
        query = REVIEW_PROCESS_BY_DOI()
        query.params = param_from_request(doi, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def fig_by_doi_idx(self, request):
        app.logger.debug(type(request))
        query = FIG_BY_DOI_IDX()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def panel_by_neo_id(self, id):
        query = PANEL_BY_NEO_ID()
        query.params = param_from_request(id, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def by_hyp(self, limit_date):
        query = BY_HYP()
        query.params = param_from_request(limit_date, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def automagic(self, limit_date):
        query = AUTOMAGIC()
        query.params = param_from_request(limit_date, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def panel_summary(self, panel_id):
        query = PANEL_SUMMARY()
        query.params = param_from_request(panel_id, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def search(self, query):
        query_lucene = LUCENE_SEARCH()
        query_lucene.params = param_from_request(query, query_lucene)  # need to know which param to extract from request depending on query.map
        # escape lucene special characters in params['query']
        text = query_lucene.params['query'] # NOTE: this makes it mandatory for the cypher SEARCH query to use the '$query' param. Not great, but that how it is.
        quoted = re.sub(r'([\+\-!\(\)\{\}\[\]\^\"~\*\?\:\\/&\|])', r'"\1"', text)
        query_lucene.params['query'] = quoted
        response_lucene = self.ask_neo(query_lucene)

        query_doi = SEARCH_DOI()
        query_doi.params = param_from_request(query, query_doi)  # need to know which param to extract from request depending on query.map
        found_doi = self.ask_neo(query_doi)
        if found_doi:
            response = found_doi
        else:
            response = response_lucene
        return json.dumps(response, indent=3)

    def covid19(self, request):
        query = COVID19()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def refereed_preprints(self, request):
        query = REFEREED_PREPRINTS()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.query2json(query)

    def refereed_preprints__plain(self, request):
        query = REFEREED_PREPRINTS()
        query.params = param_from_request(request, query)  # need to know which param to extract from request depending on query.map
        return self.ask_neo(query)
