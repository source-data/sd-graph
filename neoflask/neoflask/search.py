import json
from typing import List, Dict, NewType
from neotools.db import Instance, Query
from .queries import BY_DOI, BY_MOLECULE, BY_HYP, BY_METHOD, SEARCH

# symbolic type for a json string
json_str = NewType('json_str', str)


def param_from_request(request, query: Query) -> Dict:
    """
    Extracts from the response received by flast the values of the parameters that are required to substitute in the Query query.
    """

    params_dict = {}
    for query_var, request_param in query.map.items():
        if request_param:
            params_dict[query_var] = request.args.get(request_param[0], request_param[1]) # the value of the request param is mapped to the Query substituion variable
        else:
            assert isinstance(request, str), f"request was not a string ({request})."
            params_dict[query_var] = request # the request is a string and is the content of the Query variable
    return params_dict


class Engine:

    def __init__(self, neo4j_db: Instance):
        self.neo4j_db = neo4j_db

    def ask_neo(self, query: Query, request) -> json_str:
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            data = [r.data(*query.returns) for r in results] # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html 
            return data
        query.params = param_from_request(request, query) # need to know which param to extract from request depending on the query
        data = self.neo4j_db.query_with_tx_funct(tx_funct, query) # if query would carry params value, could be simplified to db.query(query)
        j = json.dumps(data, indent=3)
        return j

    def by_molecule(self, request):
        response = self.ask_neo(BY_MOLECULE, request)
        return response

    def by_method(self, request):
        response = self.ask_neo(BY_METHOD, request)
        return response

    def by_doi(self, request):
        response = self.ask_neo(BY_DOI, request)
        return response

    def by_hyp(self, request):
        response = self.ask_neo(BY_HYP, request)
        return response

    def search(self, request):
        response = self.ask_neo(SEARCH, request)
        return response
