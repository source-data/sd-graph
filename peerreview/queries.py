from neotools.db import Query


class MATCH_DOI(Query):

    code = '''MATCH (a:Article {doi: $doi}) RETURN DISTINCT a'''
    returns = ['a']


class NotYetPublished(Query):
    code = '''
MATCH (a:Article)
WHERE (DATETIME(a.publication_date) > DATETIME($limit_date)) AND NOT EXISTS(a.journal_doi)
RETURN DISTINCT a.doi AS doi
    '''
    map = {'limit_date': []}
    returns = ['doi']


class UpdatePublicationStatus(Query):
    code = '''
MATCH (a:Article {doi: $preprint_doi})
SET a.journal_doi = $published_doi, a.published_journal_title = $published_journal_title
RETURN a
    '''
    map = {'preprint_doi': [], 'published_doi': [], 'published_journal_title': []}
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


class REFEREED_PREPRINTS_POSTED_AFTER(Query):

    code = '''
MATCH (a:Article)
MATCH (a)-[:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
OPTIONAL MATCH (a)-->(auth:Contrib)
OPTIONAL MATCH (auth)-[:has_orcid]->(auth_id:Contrib_id)
WITH DISTINCT a, review, response, annot, auth, auth_id
WHERE review.posting_date >= $after AND review.reviewed_by = $reviewed_by
WITH
  id(a) AS id,
  a.publication_date AS pub_date,
  a.title AS title,
  a.abstract AS abstract,
  a.version AS version,
  a.doi AS doi,
  a.journalName as journal,
  COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: auth_id.text}) AS authors,
  {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: COLLECT(DISTINCT annot {.*})} AS review_process
RETURN id, pub_date, title, abstract, version, doi, journal, authors, review_process
ORDER BY pub_date DESC
    '''
    map = {'after': [], 'reviewed_by': []}
    returns = ['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'authors', 'review_process']
