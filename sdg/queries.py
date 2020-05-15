from neotools.db import Query


ALL_ARTICLES = Query(
    code='''
MATCH (a:SDArticle)
RETURN id(a) AS id, a.doi AS doi
    ''',
    returns=['id', 'doi']
)

FIGURES_BY_PAPER_ID = Query(
    code='''
MATCH (a:SDArticle )-->(f:SDFigure)
WHERE id(a) = $id
RETURN id(f) AS id, f.fig_label AS fig_label, f.href AS href, f.caption AS caption
ORDER BY f.fig_label ASC
    ''',
    map={'id': []},
    returns=['id', 'fig_label', 'href', 'caption']
)

PANEL_BY_FIG_ID = Query(
    code='''
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
    ''',
    map={'id': []},
    returns=['caption', 'formatted_caption', 'panel_label', 'panel_id', 'href', 'tags']
)