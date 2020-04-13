import re
from typing import Dict
from neo4j import GraphDatabase, Node


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

    def node(self, n: Node, clause="MERGE"):
        label = n.label
        properties_str = to_string(n.properties)
        q = Cypher(
            code=f"{clause} (n: {label} {{ {properties_str} }}) RETURN n"
        )
        record = self.query(q).single()
        node = record['n']
        return node

    def relationship(self, a, b, r: str, clause="MERGE"):
        q = Cypher(
             code=f"MATCH (a), (b) WHERE id(a)={a.id} AND id(b)={b.id} {clause} (a)-[r:{r}]->(b) RETURN r"
        )
        record = self.query(q).single()
        rel = record['r']
        return rel

    @staticmethod
    def _run_transaction(tx, q, params):
        result = tx.run(q, **params)
        return result
