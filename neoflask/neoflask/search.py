import json
from typing import List, Dict, NewType
from neotools.db import Instance, Cypher
from .queries import BY_DOI, BY_MOLECULE, BY_HYP, BY_METHOD, SEARCH

# symbolic type for a json string
json_str = NewType('json_str', str)


def param_from_request(request, query: Cypher) -> Dict:
    """
    Extracts from the response received by flast the values of the parameters that are required to substitute in the cypher query.
    """
    # simplify this: assume same name in cypher as in query, provide only default value
    params_dict = {}
    for cypher_var, request_param in query.params.items():
        if request_param:
            params_dict[cypher_var] = request.args.get(request_param[0], request_param[1]) # the value of the request param is mapped to the cypher substituion variable
        else:
            assert isinstance(request, str), f"request was not a string ({request})."
            params_dict[cypher_var] = request # the request is a string and is the content of the cypher variable
    return params_dict


class Engine:

    def __init__(self, neo4j_db: Instance):
        self.neo4j_db = neo4j_db

    def ask_neo(self, query: Cypher, request) -> json_str:
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            data = [r.data(*query.returns) for r in results] # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html 
            return data
        params = param_from_request(request, query) # need to know which param to extract from request depending on the query
        data = self.neo4j_db.query_with_tx_funct(tx_funct, query, params) # if query would carry params value, could be simplified to db.query(query)
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
