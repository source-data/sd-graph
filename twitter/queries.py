from neotools.db import Query


class ADD_TWITTER_STATUS(Query):

    code = '''
MATCH (a:Article {doi: $related_preprint_doi})
CREATE (t:Tweet)
SET t.related_preprint_doi = $related_preprint_doi
SET t.text = $text
SET t.created_at = $created_at
SET t.hastags = $hashtags
CREATE (a)-[:Twitted]->(t)
RETURN DISTINCT t
    '''
    map = {
        'related_preprint_doi': [],
        'hashtags': [],
        'text': [],
        'created_at': [],
    }
    returns = ['t']


class TWEET_BY_DOI(Query):

    code = '''
MATCH (a {doi: $doi})
WHERE (a)-[:Tweeted]->(:Tweet)
RETURN a
    '''
    map = {'doi': []}
    returns = ['doi']
