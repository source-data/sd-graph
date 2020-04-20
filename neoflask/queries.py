from neotools.db import Query


# Query queries, with the required names of the substitution variables and names of result fields
BY_DOI = Query(
    code='''
//by doi
//
MATCH (a:Article {doi: $doi})-->(author:Contrib)
OPTIONAL MATCH (author)-->(id:Contrib_id)
WITH
    a.doi AS doi,
    a.title AS title,
    a.abstract AS abstract,
    author.surname AS surname,
    author.given_names AS given_name,
    author.position_idx AS author_rank,
    author.corresp = "yes" AS corr_author,
    id.text AS ORCID
ORDER BY a.title ASC, author_rank DESC
RETURN doi, title, abstract, COLLECT([surname, given_name, ORCID, corr_author]) AS authors
''',
    map={'doi': []},
    returns=['doi', 'title', 'abstract', 'authors']
)

BY_HYP = Query(
    code='''
//by hyp
//Provides a content list based on observations and testded hypotheses.
//Returns:
//    doi: the DOI of the relevant paper
//    panel_ids: the panel_ids of the relevant panels
//    methods: the name of the method
//    controlled: the names of the controlled variables
//    measured: the names of the measured variables
//    jats_paper.publication_date as pub_date
MATCH
    (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity),
    (p)-->(i:SDTag)-->(:CondTag)-->(var_controlled:H_Entity),
    (p)-->(a:SDTag)-->(:CondTag)-->(var_measured:H_Entity),
    (p)-->(e:SDTag {category: "assay"})-->(:CondTag)-->(method:H_Entity)
WHERE
    i.role = "intervention" AND
    a.role = "assayed" AND
    var_controlled.ext_ids <> var_measured.ext_ids
WITH DISTINCT
    paper.doi AS doi,
    p.panel_id AS panel_id,
    COLLECT(DISTINCT method.name) AS methods,
    COLLECT(DISTINCT var_controlled.name) AS controlled,
    COLLECT(DISTINCT var_measured.name) AS measured,
    COUNT(DISTINCT var_controlled) AS N_1,
    COUNT(DISTINCT var_measured) AS N_2
WHERE (N_1 + N_2 > 1) OR (N_2 > 1)
MATCH (jats_paper:Article)
WHERE jats_paper.doi = doi
RETURN DISTINCT
    doi,
    COLLECT(DISTINCT panel_id) AS panel_ids,
    methods,
    controlled,
    measured,
    jats_paper.publication_date as pub_date
ORDER BY pub_date DESC
''',
    returns=['doi', 'panel_ids', 'methods', 'controlled', 'measured', 'pub_date']
)

BY_METHOD = Query(
    code='''
//by method
MATCH
  (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity),
  (p)-->(e:SDTag {category: "assay"})-->(:CondTag)-->(method:H_Entity)
WHERE e.ext_ids <> ""
WITH DISTINCT
  paper.doi AS doi,
  method.name AS item_name,
  [method.ext_ids] as item_ids,
  COLLECT(DISTINCT p.panel_id) AS panel_ids
RETURN
  item_name,
  item_ids,
  COLLECT(DISTINCT {doi: doi, panel_ids: panel_ids}) AS content_ids,
  COUNT(DISTINCT doi) AS score
ORDER BY score DESC
''',
    returns=['item_name', 'item_ids', 'content_ids', 'score']
)

BY_MOLECULE = Query(
    code='''
//by molecule
MATCH
  (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(mol:H_Entity)
WHERE
  (mol.type = "gene" OR mol.type = "protein" OR mol.type = "molecule") AND
  (ct.role = "intervention" OR ct.role = "assayed" OR ct.role = "experiment")
WITH DISTINCT
  paper.doi AS doi,
  mol.name AS item_name,
  COLLECT(DISTINCT mol.ext_ids) AS item_ids,
  COLLECT(DISTINCT p.panel_id) AS panel_ids
RETURN
  item_name,
  item_ids,
  COLLECT(DISTINCT {doi: doi, panel_ids: panel_ids}) AS content_ids,
  COUNT(DISTINCT doi) AS score
ORDER BY score DESC
''',
    returns=['item_name', 'item_ids', 'content_ids', 'score']
)


SEARCH = Query(
    code='''
//search
// Full-text search on multiple indices.
//CALL db.index.fulltext.createNodeIndex("title", ["Article"], ["title"]);
CALL db.index.fulltext.queryNodes("title", $query) YIELD node, score
WITH node.doi AS doi, node.title as text, score, "title" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

//CALL db.index.fulltext.createNodeIndex("abstract",["Article"], ["abstract"]);
CALL db.index.fulltext.queryNodes("abstract", $query) YIELD node, score
WITH node.doi AS doi, node.title as text, score, "abstract" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

//CALL db.index.fulltext.createNodeIndex("caption",["Fig"], ["caption"]);
CALL db.index.fulltext.queryNodes("caption", $query) YIELD node, score
MATCH (article:Article)-[:has_figure]->(node)
WITH article.doi as doi, node.caption as text, score, "caption" AS source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

//CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname"]);
CALL db.index.fulltext.queryNodes("name", $query) YIELD node, score
MATCH (article:Article)-->(author:Contrib)
WHERE author.surname = node.surname
WITH DISTINCT article.doi as doi, node.surname as text, score, "author" AS source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

//CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"]);
CALL db.index.fulltext.queryNodes("entity_name", $query) YIELD node, score
WHERE node.name <> ""
MATCH (sd_article:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity)
WHERE h.name = node.name
WITH DISTINCT sd_article.doi as doi, h.name as text, score, "entity" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

//CALL db.index.fulltext.createNodeIndex("synonym",["Term"],["text"]);
CALL db.index.fulltext.queryNodes("synonym", $query) YIELD node, score
MATCH (sd_article:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity)-->(te:Term)
WHERE te.text = node.text
WITH DISTINCT sd_article.doi as doi, te.text as text, score, "synonym" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)
''',
    map={'query': ['query', ''], 'limit': ['limit', 10]},
    returns=['doi', 'text', 'score', 'source']
)
