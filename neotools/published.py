'''
update published status of nodes :Article
'''

from neotools.db import Query

class AllDois(Query):
    code = '''
MATCH (a:Article)
RETURN DISTINCT a.doi
    '''
    returns = ['doi']


class UpdatePublishedStatus(Query):
    code = '''
MATCH (a:Article {doi: $doi})
SET a.publihshed = $published
RETURN a
    '''
    map = {'doi': []},
    returns = ['a']


class Publish
def get_all_dois():
    results = self.db.query(AllDois())
    dois = results.get('doi')
    return dois


def published(doi):
    published = biorxiv.details(doi).get('published', None)
    return published is not None


def update_satus(doi):
    update_published_status = UpdatePublishedStatus(params={'doi': doi})
    db.query(update_published_status)

def ():
    doid = get_all_dois()
    for doi in dois:
        if published(doi)
            update_status(doi, published)

