from typing import Dict
from neotools.db import Instance, Query


class Engine:
    """
    Handle requests received from the Flask app, make respective database queries and returns the results.

    Arguments:
        neo4j_db (Instance): a neotools.db.Instance that connects to the database and handles transactions
    """
    def __init__(self, neo4j_db: Instance):
        self.neo4j_db = neo4j_db

    def ask_neo(self, query: Query, **kwargs) -> Dict:
        """
        Run a query and return the database results as dictionary with the keys specified in the query.returns list.
        """
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            data = [r.data(*query.returns) for r in results]  # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html
            return data
        # use the map of name of substitution variable in cypher to the name and default value of the var in the request
        for var_in_cypher, var_in_request in query.map.items():
            query.params[var_in_cypher] = kwargs.get(var_in_request['req_param'], var_in_request['default'])
        data = self.neo4j_db.query_with_tx_funct(tx_funct, query)
        return data
