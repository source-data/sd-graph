from neotools.db import Query


class SOURCE_BY_UUID(Query):

    code = '''MATCH (n:Article {source: $source}) RETURN n;'''
    map = {'source': ['source', '']}
    returns = ['n']


class CREATE_INDEX_DOI(Query):

    code = '''CREATE INDEX ON :Article(doi);'''


class CREATE_INDEX_VERSION(Query):

    code = '''CREATE INDEX ON :Article(version);'''
