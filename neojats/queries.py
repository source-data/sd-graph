
from neotools.db import Query


SOURCE_BY_UUID = Query(
    code='''MATCH (n:Article {source: $source}) RETURN n;''',
    map={'source': ['source', '']},
    returns=['n']
)

CREATE_FULLTEXT_INDEX_ON_TITLE = Query(
    code='''CALL db.index.fulltext.createNodeIndex("title", ["Article"], ["title"]);'''
)
CREATE_FULLTEXT_INDEX_ON_ABSTRACT = Query(
    code='''CALL db.index.fulltext.createNodeIndex("abstract", ["Article"], ["abstract"]);'''
)
CREATE_FULLTEXT_INDEX_ON_CAPTION = Query(
    code='''CALL db.index.fulltext.createNodeIndex("caption", ["Fig"], ["caption"]);'''
)
CREATE_FULLTEXT_INDEX_ON_NAME = Query(
    code='''CALL db.index.fulltext.createNodeIndex("name", ["Contrib"], ["surname"]);'''
)

# TODO: neo4j index of doi + version