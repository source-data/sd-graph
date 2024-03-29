from neotools.db import Query


class SOURCE_BY_UUID(Query):

    code = '''MATCH (n:Article {source: $source}) RETURN n;'''
    map = {'source': ['source', '']}
    returns = ['n']


class CREATE_INDEX_DOI(Query):

    code = '''CREATE INDEX article_doi IF NOT EXISTS FOR (n:Article) ON (n.doi);'''


class CREATE_INDEX_VERSION(Query):

    code = '''CREATE INDEX article_version IF NOT EXISTS FOR (n:Article) ON (n.version);'''


class FIND_RESPONSE(Query):
    code = '''MATCH (r:Response {related_article_doi: $related_article_doi}) RETURN r;'''
    map = {'related_article_doi': ['related_article_doi', '']}
    returns = ['r']


class FIND_REVIEW(Query):
    code = '''MATCH (r:Review {related_article_doi: $related_article_doi, review_idx: $review_idx}) RETURN r;'''
    map = {
        'related_article_doi': ['related_article_doi', ''],
        'review_idx': ['review_idx', ''],
    }
    returns = ['r']
