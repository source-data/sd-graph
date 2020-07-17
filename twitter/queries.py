from neotools.db import Query


class ADD_TWITTER_STATUS(Query):

    code = '''
CREATE (t:Tweet)
SET t.related_preprint_doi = $related_preprint_doi
SET t.text = $text
SET t.created_at = $created_at
SET t.hastags = $hashtags
SET t.twitter_id = $twitter_id
WITH t
MATCH (a:Article {doi: $related_preprint_doi})
WITH a, t
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
MATCH (a {doi: $doi})-[:Twitted]->(t:Tweet)
RETURN DISTINCT t
    '''
    map = {'doi': []}
    returns = ['t']


class DELETE_TWEET(Query):

    code = '''
MATCH (t:Tweet {twitter_id: $twitter_id})-[r]-()
DELETE r, t
RETURN DISTINCT COUNT(DISTINCT t) AS N_updates, COUNT(DISTINCT r) AS N_rel
    '''
    map = {'twitter_id': []}
    returns = ['N_updates', 'N_rel']


class ALL_TWEETS(Query):
    code = '''
MATCH (t:Tweet)
RETURN t{.*} as tweet
    '''
    returns = ['tweet']


class TWEET_BY_ID(Query):
    code = '''
MATCH (t:Tweet {twitter_id: $twitter_id})
RETURN t
    '''
    map = {'twitter_id': []}
    returns = ['t']
