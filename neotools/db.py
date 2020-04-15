import re
from typing import Dict, Callable
from neo4j import GraphDatabase, Node, BoltStatementResult, BoltStatementResultSummary, Session, Transaction


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


class Cypher:
    def __init__(self, code: str = '', params: Dict = {}, returns: Dict = {}):
        self.code = code
        self.params = params
        self.returns = returns
        substitution_variables = re.findall(r"\$(\w+)", self.code)
        # check that parameters needed appear in the cypher code
        for p in self.params:
            assert p in substitution_variables, f"variable '{p}' missing in {substitution_variables} extracted from the cypher code \"{self.code}\""


class Instance:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, q: Cypher, params={}):
        with self._driver.session() as session:
            results = session.write_transaction(self._run_transaction, q.code, params)
            return results

    def query_with_tx_funct(self, tx_funct: Callable, q: Cypher, params={}):
        # To enable consuming results within session according to https://neo4j.com/docs/api/python-driver/current/transactions.html
        # "Results should be fully consumed within the function and only aggregate or status values should be returned"
        with self._driver.session() as session:
            results = session.write_transaction(tx_funct, q.code, params)
            return results

    def node(self, n: Node, clause="MERGE"):
        label = n.label
        properties_str = to_string(n.properties)
        q = Cypher(
            code=f"{clause} (n: {label} {{ {properties_str} }}) RETURN n;"
        )
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        node = res['n']
        return node

    def relationship(self, a, b, r: str, clause="MERGE"):
        q = Cypher(
            code=f"MATCH (a), (b) WHERE id(a)={a.id} AND id(b)={b.id} {clause} (a)-[r:{r}]->(b) RETURN r;"
        )
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        rel = res['r']
        return rel

    @staticmethod
    def _tx_funct_single(tx, q, params={}):
        results: BoltStatementResult = tx.run(q)
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
    def _run_transaction(tx, q, params):
        result = tx.run(q, **params)
        return result
