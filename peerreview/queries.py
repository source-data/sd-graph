from neotools.db import Query


class MATCH_DOI(Query):

    code = '''MATCH (a:Article {doi: $doi}) RETURN DISTINCT a'''
    returns = ['a']


class LINK_REVIEWS(Query):

    code = '''
MATCH (review:Review), (a:Article)
WHERE review.related_article_doi = a.doi
WITH review, a
MERGE (a)-[r:HasReview]->(review)
RETURN COUNT(DISTINCT r) AS N
    '''
    returns = ['N']


class LINK_RESPONSES(Query):

    code = '''
MATCH (response:Response), (a:Article)
WHERE response.related_article_doi = a.doi
WITH response, a
MERGE (a)-[r:HasResponse]->(response)
RETURN COUNT(DISTINCT r) AS N
    '''
    returns = ['N']


class LINK_ANNOT(Query):

    code = '''
MATCH (annot:PeerReviewMaterial), (a:Article)
WHERE annot.related_article_doi = a.doi
WITH annot, a
MERGE (a)-[r:HasAnnot]->(annot)
RETURN COUNT(DISTINCT r) AS N
    '''
    returns = ['N']
