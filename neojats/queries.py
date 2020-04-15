
from neotools.db import Cypher


SOURCE_BY_UUID = Cypher(
    code='''MATCH (n:Article {source: $source}) RETURN n;''',
    params={'source': ['source', '']},
    returns=['n']
)

CREATE_FULLTEXT_INDEX = Cypher(
    code='''
CALL db.index.fulltext.createNodeIndex("title",["Article"], ["title"]);
CALL db.index.fulltext.createNodeIndex("abstract",["Article"], ["abstract"]);
CALL db.index.fulltext.createNodeIndex("caption",["Fig"], ["caption"]);
CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname"]);
'''
)