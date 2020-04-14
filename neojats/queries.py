
from neotools.db import Cypher

SOURCE_BY_UUID = Cypher(
    code = '''MATCH (n:Article {source: $source}) RETURN n;''',
    params = {'source': ['source', '']},
    returns = ['n']
)