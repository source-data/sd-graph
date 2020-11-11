from neotools.db import Query


class ALL_ARTICLES(Query):

    code = '''
MATCH (a:SDArticle)
RETURN id(a) AS id, a.doi AS doi
    '''
    returns = ['id', 'doi']


class FIGURES_BY_PAPER_ID(Query):

    code = '''
MATCH (a:SDArticle )-->(f:SDFigure)
WHERE id(a) = $id
RETURN id(f) AS id, f.fig_label AS fig_label, f.fig_title as fig_title, f.href AS href, f.caption AS caption
ORDER BY f.fig_label ASC
    '''
    map = {'id': []}
    returns = ['id', 'fig_label', 'fig_title', 'href', 'caption']


class PANEL_BY_FIG_ID(Query):

    code = '''
MATCH (f:SDFigure)-->(p:SDPanel)-->(t:SDTag)
WHERE id(f) = $id AND t.in_caption = true
WITH 
    p.caption AS caption, 
    p.formatted_caption AS formatted_caption,
    p.panel_label AS panel_label, 
    p.panel_id AS panel_id, 
    p.href AS href, 
    COLLECT(DISTINCT t) AS tags
RETURN caption, panel_label, panel_id, href, tags
ORDER BY panel_label ASC
    '''
    map = {'id': []}
    returns = ['caption', 'formatted_caption', 'panel_label', 'panel_id', 'href', 'tags']


class SDARTICLE_LOADING_STATUS(Query):

    code = '''
MATCH (a:SDArticle {doi: $doi})
RETURN a.status as status
    '''
    map = {'doi': []}
    returns = ['status']


class COLLECTION_NAMES(Query):
    code = '''
MATCH (subject:Subject)
RETURN DISTINCT subject.text AS subject
    '''
    returns = ['subject']


class DELETE_TREE(Query):
    code = '''
MATCH (a:SDArticle {doi: $doi})-[r1]->(f:SDFigure)-[r2]->(p:SDPanel)-[r3]->(t:SDTag)
WITH a, f, p, t, r1, r2, r3
DELETE r3
WITH a, f, p, t, r1, r2
DELETE t
WITH a, f, p, r1, r2
DELETE r2
WITH a, f, p, r1
DELETE p
WITH a, f, r1
DELETE r1
WITH a, f
DELETE f
WITH a
DELETE a
RETURN COUNT(DISTINCT a) AS article_deleted
    '''
    map = {'doi': []}
    returns = ['article_deleted']


class SET_STATUS(Query):
    code = '''
    MATCH (a:SDArticle {doi: $doi})
    SET a.status = $status
    RETURN a
    '''
    map = {'doi': [], 'status': []}
    returns = ['a']
