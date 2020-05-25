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
RETURN id(f) AS id, f.fig_label AS fig_label, f.fig_title as fig_title, f.href AS href, f.caption AS caption
ORDER BY f.fig_label ASC
    ''',
    map={'id': []},
    returns=['id', 'fig_label', 'fig_title', 'href', 'caption']
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

RANK_SUM = Query(
    code='''
// rank sum
// rank sum
MATCH (a:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(t:CondTag)
WHERE 
    (t.category = 'assay')
WITH DISTINCT a, tolower(t.text) AS tag_text, COUNT(DISTINCT p) AS repeats
WHERE repeats > 1
WITH DISTINCT 
    a, 
    COLLECT(DISTINCT tag_text) AS methods,
    COUNT(DISTINCT tag_text) AS N
ORDER BY N DESC
//LIMIT 100
WITH COLLECT({title: a.title, terms: methods, freq:N}) as preprint_list
WITH preprint_list, range(1, size(preprint_list)) AS index
UNWIND index as i
WITH COLLECT({rank: i, preprint: preprint_list[i]}) AS ranked_by_method

MATCH (a:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(t:CondTag)
WHERE 
    (t.type = 'geneprod' OR t.type ='small_molecule')
WITH DISTINCT a, tolower(t.text) AS tag_text, COUNT(DISTINCT p) AS repeats, ranked_by_method
WHERE repeats > 1
WITH DISTINCT 
    a, 
    COLLECT(DISTINCT tag_text) AS molecules,
    COUNT(DISTINCT tag_text) AS N,
    ranked_by_method
ORDER BY N DESC
//LIMIT 100
WITH COLLECT({title: a.title, terms: molecules, freq:N}) as preprint_list, ranked_by_method
WITH preprint_list, range(1, size(preprint_list)) AS index, ranked_by_method
UNWIND index as i
WITH COLLECT({rank: i, preprint: preprint_list[i]}) AS ranked_by_molecule, ranked_by_method
WHERE (ranked_by_molecule <> []) AND (ranked_by_method <> [])
WITH ranked_by_molecule + ranked_by_method AS ranked
UNWIND ranked as item
WITH DISTINCT item.preprint.title AS title, COLLECT(item.preprint.terms) AS items, COLLECT(item.rank) AS ranks, SUM(item.rank) AS rank_sum
WHERE size(items) = 2
RETURN title, items, ranks, rank_sum
ORDER BY rank_sum ASC
LIMIT 10
    '''
)

DOMINANT_HYP = Query(
    code='''
// dominant hyp
MATCH 
    (a:SDArticle)-->(f:SDFigure)-->(p:SDPanel),
    (p)-->(ctrl_v:CondTag {role: "intervention"}),
    (p)-->(meas_v:CondTag {role: "assayed"})
OPTIONAL MATCH
  (p)-->(assay:CondTag {category: "assay"})
WHERE
  toLower(ctrl_v.text) <> toLower(meas_v.text)
WITH DISTINCT
  a,
  [toLower(ctrl_v.text), toLower(meas_v.text)] AS hyp,
  COLLECT(DISTINCT toLower(assay.text)) AS assays,
  COUNT(DISTINCT p) AS N_panels
WHERE N_panels > 1
WITH a, hyp, N_panels, assays, size(assays) AS N_assays
ORDER BY N_panels DESC
RETURN
  a.title,
  assays,
  N_assays,
  COLLECT(hyp)[0] AS dominant,
  COLLECT(N_panels)[0] AS N
ORDER BY N_assays DESC
LIMIT 10
    '''
)