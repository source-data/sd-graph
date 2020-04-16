import re
from typing import Dict, Callable
from neo4j import GraphDatabase, Node, BoltStatementResult, BoltStatementResultSummary, Transaction


def quote4neo(attributes):
    quotes_added = {}
    for k, v in attributes.items():
        if v is None:
            v = '""'
        elif isinstance(v, str):
            v = v.replace("'", r"\'")
            v = v.replace('"', r"'")
            v = v.replace('\\', r'\\')
            v = f'"{v}"'
        quotes_added[k] = v
    return quotes_added


def to_string(properties):
    properties = quote4neo(properties)  # add quotes for neo cypher queries
    properties_str = ', '.join([f"{k}: {v}" for k, v in properties.items()]) # stringfy
    return properties_str


class Query:
    def __init__(self, code: str = '', map: Dict = {}, params: Dict = {}, returns: Dict = {}):
        """
        A simplistic abstraction of a query. 

        Args:
            code (str): the string of the query
            map (Dict(str, List[str, str])): the mapping between the variable in the query (key) and a list with the name of the request parameter and its default value
            params (Dict): the value of each parameters to be forwarded in the database transaction
            returns (List): the keys to use when retrieving the results
        """
        self.code = code
        self.map = map  # rename this into param_map args_map and reserve params to the actual value
        self.params = params
        self.returns = returns
        substitution_variables = re.findall(r"\$(\w+)", self.code)
        # check that parameters needed appear in the code
        for p in self.map:
            assert p in substitution_variables, f"variable '${p}' missing in from the query code \"{self.code}\""
        # checking for returns is more annoying: parse cypher between RETURN and next expected Cypher clause


class Instance:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, q: Query):
        with self._driver.session() as session:
            results = session.write_transaction(self._run_transaction, q.code, q.params)  # would be nicer to have q.code, q.params
            return results

    def query_with_tx_funct(self, tx_funct: Callable, q: Query):
        # To enable consuming results within session according to https://neo4j.com/docs/api/python-driver/current/transactions.html
        # "Results should be fully consumed within the function and only aggregate or status values should be returned"
        with self._driver.session() as session:
            results = session.write_transaction(tx_funct, q.code, q.params)
            return results

    def node(self, n: Node, clause="MERGE"):
        label = n.label
        properties_str = to_string(n.properties)
        q = Query(
            code=f"{clause} (n: {label} {{ {properties_str} }}) RETURN n;"
        )
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        node = res['n']
        return node

    def relationship(self, a, b, r: str, clause="MERGE"):
        q = Query(
            code=f"MATCH (a), (b) WHERE id(a)={a.id} AND id(b)={b.id} {clause} (a)-[r:{r}]->(b) RETURN r;"
        )
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        rel = res['r']
        return rel

    @staticmethod
    def _tx_funct_single(tx: Transaction, code: str, params: Dict = {}):
        results: BoltStatementResult = tx.run(code)
        records = [r for r in results] # consume results right here
        if len(records) > 1:
            summary: BoltStatementResultSummary = results.summary()
            print(f"WARNING: {len(records)} > 1 records returned with statement:'")
            print(summary.statement)
            print(f"with params {summary.parameters}.")
            print("Affected records:")
            for r in records:
                print(r)
        r = records[0]
        return r

    @staticmethod
    def _run_transaction(tx: Transaction, code: str, params: Dict):
        result = tx.run(code, params)
        return result
