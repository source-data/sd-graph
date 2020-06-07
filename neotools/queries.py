from neotools.db import Query


SOURCE_BY_UUID = Query(
    code='''MATCH (n:Article {source: $source}) RETURN n;''',
    map={'source': ['source', '']},
    returns=['n']
)

CREATE_INDEX_DOI = Query(
    code='''CREATE INDEX ON :Article(doi);'''
)

CREATE_INDEX_VERSION = Query(
    code='''CREATE INDEX ON :Article(version);'''
)
