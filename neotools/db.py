import re
from typing import List, Dict, Tuple, Callable
from neo4j import GraphDatabase, Node, BoltStatementResult, BoltStatementResultSummary, Transaction


def quote4neo(properties):
    quotes_added = {}
    for k, v in properties.items():
        if v is None:
            v = '""'
        elif isinstance(v, str):
            v = v.replace("'", r"\'")
            v = v.replace('"', r"'")
            v = v.replace('\\', r'\\') # why?
            v = f'"{v}"'
        quotes_added[k] = v
    return quotes_added


def to_string(properties):
    properties = quote4neo(properties)  # add quotes for neo cypher queries
    properties_str = ', '.join([f"{k}: {v}" for k, v in properties.items()]) # stringfy
    return properties_str


class Query:

    code = ''
    map = {}
    returns = {}

    def __init__(self, params: Dict = {}):
        """
        A simplistic class for a query. 

        Class attributes:
            code (str): the string of the query
            map (Dict(str, List[str, str])): the mapping between the variable in the query (key) and a list with the name of the request parameter and its default value
            returns (List): the keys to use when retrieving the results

        Args:
            params (Dict): the value of each parameters to be forwarded in the database transaction
        """
        self.params = params
        substitution_variables = re.findall(r"\$(\w+)", self.code)
        # check that parameters needed appear in the code
        for p in self.map:
            assert p in substitution_variables, f"variable '${p}' missing in from the query code \"{self.code}\""
        # checking for returns is more annoying: parse cypher between RETURN and next expected Cypher clause

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, p: Dict):
        self._params = p


class Instance:

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password)) #, encrypted=True)

    def close(self):
        self._driver.close()

    def query(self, q: Query):
        with self._driver.session() as session:
            results = session.write_transaction(self._tx_funct, q.code, q.params)
            return results

    def query_with_tx_funct(self, tx_funct: Callable, q: Query):
        # To enable consuming results within session according to https://neo4j.com/docs/api/python-driver/current/transactions.html
        # "Results should be fully consumed within the function and only aggregate or status values should be returned"
        with self._driver.session() as session:
            results = session.write_transaction(tx_funct, q.code, q.params)
            return results

    def exists(self, q: Query) -> bool:
        def tx_funct(tx, code, params):
            results = tx.run(code, params)
            found_one = results.single() is not None
            summary = results.summary()
            notifications = summary.notifications
            if notifications:
                print(f"WARNING: {notifications} when checking for existance.")
                print(summary.statement)
                print(summary.parameters)
            return found_one
        found_it = self.query_with_tx_funct(tx_funct, q)
        return found_it

    def node(self, n: Node, clause="MERGE"):
        # avoid direct code injection via clause
        if clause == 'MERGE':
            cl = 'MERGE'
        elif clause == 'CREATE':
            cl = 'CREATE'
        else:
            clause = None
        label = n.label
        properties_str = to_string(n.properties)  # CHANGE THIS into params={**properties}
        q = Query()
        q.code = f"{cl} (n: {label} {{ {properties_str} }}) RETURN n;"
        q.returns = ['n']
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        node = res['n']
        return node

    def relationship(self, a, b, r: str, clause="MERGE"):
        # avoid direct code injection
        if clause == 'MERGE':
            cl = 'MERGE'
        elif clause == 'CREATE':
            cl = 'CREATE'
        else:
            clause = None
        q = Query()
        q.code = f"MATCH (a), (b) WHERE id(a)={a.id} AND id(b)={b.id} {cl} (a)-[r:{r}]->(b) RETURN r;"
        q.returns = ['r']
        res = self.query_with_tx_funct(self._tx_funct_single, q)
        rel = res['r']
        return rel

    def batch_of_nodes(self, label: str, batch: List[Dict]):
        # {batch: [{name:"Alice",age:32},{name:"Bob",age:42}]}
        records = []
        if batch:
            q = Query()
            q.code = f'''
                    UNWIND $batch AS row
                    CREATE (n:{label})
                    SET n += row
                    RETURN n
                    '''
            q.returns = ['n']
            q.params = {'batch': batch}
            records = self.query_with_tx_funct(self._tx_funct, q)
            nodes = [r['n'] for r in records]
        return nodes

    def batch_of_relationships(self, batch: List[Tuple[Node, Node]], rel_label: str = '', clause="CREATE"):
        records = []
        if batch:
            q = Query()
            q.code = f'''
                    UNWIND $batch AS row
                    MATCH (s), (t) WHERE id(s) = row.source AND id(t) = row.target
                    {clause} (s) -[r:{rel_label}]-> (t)
                    RETURN r
                    '''
            q.returns = ['r']
            q.params = {'batch': batch}
            records = self.query_with_tx_funct(self._tx_funct, query)
            relationships = [r['r'] for r in records]
        return relationships

    @staticmethod
    def _tx_funct_single(tx: Transaction, code: str, params: Dict = {}):
        records = Instance._tx_funct(tx, code, params)
        if len(records) > 1:
            print(f"WARNING: {len(records)} > 1 records returned with statement:'")
            print(code)
            print(f"with params {params}.")
            print("Affected records:")
            for r in records:
                print(r)
        r = records[0]
        return r

    @staticmethod
    def _tx_funct(tx: Transaction, code: str, params: Dict = {}):
        # To enable consuming results within session according to https://neo4j.com/docs/api/python-driver/current/transactions.html
        # "Results should be fully consumed within the function and only aggregate or status values should be returned"
        results: BoltStatementResult = tx.run(code, params)
        records = list(results)
        return records
