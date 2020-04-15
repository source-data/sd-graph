
from neotools.db import Cypher


SOURCE_BY_UUID = Cypher(
    code='''MATCH (n:Article {source: $source}) RETURN n;''',
    params={'source': ['source', '']},
    returns=['n']
)

CREATE_FULLTEXT_INDEX_ON_TITLE = Cypher(
    code='''CALL db.index.fulltext.createNodeIndex("title", ["Article"], ["title"]);'''
)
CREATE_FULLTEXT_INDEX_ON_ABSTRACT = Cypher(
    code='''CALL db.index.fulltext.createNodeIndex("abstract", ["Article"], ["abstract"]);'''
)
CREATE_FULLTEXT_INDEX_ON_CAPTION = Cypher(
    code='''CALL db.index.fulltext.createNodeIndex("caption", ["Fig"], ["caption"]);'''
)
CREATE_FULLTEXT_INDEX_ON_NAME = Cypher(
    code='''CALL db.index.fulltext.createNodeIndex("name", ["Contrib"], ["surname"]);'''
)
