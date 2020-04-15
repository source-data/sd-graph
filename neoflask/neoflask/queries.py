from neotools.db import Cypher


# Cypher queries, with the required names of the substitution variables and names of result fields
BY_DOI = Cypher(
    code='''MATCH (a:Article {doi: $doi})-->(author:Contrib)
OPTIONAL MATCH (author)-->(id:Contrib_id)
WITH 
    a.title AS title, 
    a.abstract AS abstract, 
    author.surname AS surname, 
    author.given_names AS given_name, 
    author.position_idx AS author_rank,
    author.corresp = "yes" AS corr_author,
    id.text AS ORCID
ORDER BY a.title ASC, author_rank DESC
RETURN title, abstract, COLLECT([surname, given_name, ORCID, corr_author]) AS auth
''',
    params={'doi': []},
    returns=['title', 'abstract', 'auth']
)

BY_HYP = Cypher(
    code='''
// by hyp v4
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
  paper,
  p,
  COLLECT(DISTINCT method.name) AS methods, 
  COLLECT(DISTINCT var_controlled.name) AS controlled_variables, 
  COLLECT(DISTINCT var_measured.name) AS measured_variables,
  COUNT(DISTINCT var_controlled) AS N_1,  
  COUNT(DISTINCT var_measured) AS N_2
WHERE (N_1 + N_2 > 1) OR (N_2 > 1)
MATCH (jats_paper:Article)
WHERE jats_paper.doi = paper.doi
WITH DISTINCT p, methods, controlled_variables, measured_variables, jats_paper.doi AS doi, jats_paper.publication_date as pub_date
RETURN 
  doi, pub_date, COLLECT(DISTINCT p.panel_id) AS panel_ids, methods, controlled_variables, measured_variables
ORDER BY pub_date DESC''',
returns=['doi', 'pub_date', 'panel_ids', 'methods', 'controlled_variables', 'measured_variables']

)

BY_METHOD = Cypher(
    code='''
// by method
MATCH
  (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity),
  (p)-->(e:SDTag {category: "assay"})-->(:CondTag)-->(method:H_Entity)
WHERE e.ext_ids <> ""
WITH DISTINCT
  paper.doi AS doi, 
  method.name AS method_names, method
RETURN 
  method_names, method.ext_ids AS method_id, COLLECT(DISTINCT paper.doi) AS doi, COUNT(DISTINCT doi) AS popularity
ORDER BY popularity DESC
''',
    returns=['method_names', 'method_id', 'doi']
)

BY_MOLECULE = Cypher(
    code='''
// by molecule
MATCH
  (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(mol:H_Entity)
WHERE 
  (mol.type = "gene" OR mol.type = "protein" OR mol.type = "molecule") AND
  (ct.role = "intervention" OR ct.role = "assayed" OR ct.role = "experiment")
RETURN DISTINCT 
  mol.name AS molecule,
  COLLECT(DISTINCT mol.ext_ids) AS mol_ids,
  COLLECT(DISTINCT paper.doi) AS doi,
  COUNT(DISTINCT paper) AS popularity
ORDER BY popularity DESC
''',
    returns=['molecule', 'mol_ids', 'doi', 'popularity']
)


SEARCH = Cypher(
    code='''
/// Full-text search on the index created with:
// CALL db.index.fulltext.createNodeIndex("titles_captions_names",["SDArticle"],["title"])
CALL db.index.fulltext.queryNodes("titles_captions_names", $query) YIELD node, score
WHERE node.doi <> ""
WITH node.doi AS doi, node.title as text, score, "title" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

CALL db.index.fulltext.queryNodes("titles_captions_names", $query) YIELD node, score
WHERE node.panel_id <> ""
WITH node, score
MATCH (article_from_panel:SDArticle)-->(f:SDFigure)-->(p:SDPanel {panel_id:node.panel_id})
WITH article_from_panel.doi as doi, p.formatted_caption as text, score, "caption" AS source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)

UNION

CALL db.index.fulltext.queryNodes("titles_captions_names", $query) YIELD node, score
WHERE node.ext_ids <> ""
WITH node, score
MATCH (article_from_entity:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity {ext_ids: node.ext_ids})
WITH article_from_entity.doi as doi, h.name as text, score, "entity" as source
RETURN doi, text, score, source
ORDER BY score DESC
LIMIT toInteger($limit)
''',
    params={'query': ['query', ''], 'limit': ['limit', 10]},
    returns=['doi', 'text', 'score', 'source']
)

