import os
from pathlib import Path
from dotenv import load_dotenv
from neotools.db import Instance, Query
from typing import Dict

load_dotenv()
def get_db():
    NEO_URI = os.getenv('NEO_URI')
    NEO_USERNAME = os.getenv("NEO_USERNAME")
    NEO_PASSWORD = os.getenv("NEO_PASSWORD")
    return Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)


def ask_neo(query: Query, **kwargs) -> Dict:
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
    data = get_db().query_with_tx_funct(tx_funct, query)
    return data
