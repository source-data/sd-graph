import json
from typing import List, Dict, NewType
from neotools.db import Instance, Cypher
from .queries import BY_DOI, BY_MOLECULE, BY_HYP, BY_METHOD, SEARCH

# symbolic type for a json string
json_str = NewType('json_str', str)

def param_from_request(request, query:Cypher) -> Dict:
    """
    Extracts from the response received by flast the values of the parameters that are required to substitute in the cypher query.
    """
    params_dict = {}
    for cypher_var, request_param in query.params.items():
        if request_param:
            params_dict[cypher_var] = request.args.get(request_param[0], request_param[1]) # the value of the request param is mapped to the cypher substituion variable
        else:
            assert isinstance(request, str), f"request was not a string ({request})."
            params_dict[cypher_var] = request # the request is a string and is the content of the cypher variable
    return params_dict

def neo2response(results, query:Cypher) -> Dict:
    """
    Extracts the values returned by the database so that they can be used to build the response of of the flask server.
    """
    response = []
    for record in results.records():
        row = {}
        for key in query.returns:
            row[key] = record[key]
        response.append(row)
    return response

class Engine:

    def __init__(self, neo4j_db:Instance):
        self.neo4j_db = neo4j_db

    def ask_neo(self, query:Cypher, request) -> json_str:
        params = param_from_request(request, query) # need to know which param to extract from request depending on the query
        results = self.neo4j_db.query(query, params)
        response = neo2response(results, query)
        j = json.dumps(response, indent=3)
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
