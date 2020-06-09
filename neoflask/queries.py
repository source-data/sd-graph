from neotools.db import Query


COVID19 = Query(
    code='''
// COVID-19
// Automated search for COVID-19 / SARS-CoV-2 papers
WITH
    "2019 Novel Coronavirus OR 2019-nCoV OR 2019nCoV OR COVID-19 OR SARS-CoV-2 OR SARS-CoV2 OR SAR-CoV2 OR SRAS-CoV-2 OR (wuhan AND coronavirus)" AS search_query
CALL db.index.fulltext.queryNodes("abstract", search_query) YIELD node, score
WITH node.doi AS doi, node.version AS version, node, score
ORDER BY score DESC, version DESC
WITH DISTINCT doi, COLLECT(node) AS versions, COLLECT(score) AS scores
WHERE scores[0] > 0.02
WITH doi, versions[0] AS most_recent, scores[0] AS score
MATCH (a:Article {doi:doi, version: most_recent.version})-->(f:Fig)
RETURN
    id(a) AS id,
    a.publication_date AS pub_date,
    a.title AS title,
    a.abstract AS abstract,
    a.version AS version,
    a.doi AS doi,
    'bioRxiv' AS journal,
    COUNT(DISTINCT f) AS nb_figures,
    score
ORDER BY pub_date DESC, score DESC;
    ''',
    map={},
    returns=['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'nb_figures', 'score']
)

REFEREED_PREPRINTS = Query(
  code='''
MATCH (a:Article)
OPTIONAL MATCH (a)-[:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH
  id(a) AS id,
  a.publication_date AS pub_date,
  a.title AS title,
  a.abstract AS abstract,
  a.version AS version,
  a.doi AS doi,
  a.journalName as journal,
  {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process
WHERE
  review_process.reviews <> [] OR EXISTS(review_process.annot)
RETURN id, pub_date, title, abstract, version, doi, journal, review_process
ORDER BY pub_date DESC
  ''',
  returns=['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'nb_figures', 'review_process']
)

BY_DOI = Query(
    code='''
//by doi
//
MATCH (preprint:Article {doi: $doi})
WITH preprint, preprint.version AS version
ORDER BY version DESC
WITH COLLECT(preprint)[0] AS a
MATCH
   (a)-->(auth:Contrib)
OPTIONAL MATCH (auth)-->(id:Contrib_id)
OPTIONAL MATCH (a)-->(f:Fig)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH DISTINCT
    id(a) AS id,
    a.doi AS doi,
    a.version AS version,
    a.source AS source,
    a.journal_title AS journal,
    a.title AS title,
    a.abstract AS abstract,
    a.publication_date AS pub_date,
    auth,
    id.text AS ORCID,
    COUNT(DISTINCT f) AS nb_figures,
    review, response, annot
ORDER BY
    review.review_idx ASC, 
    auth.position_idx ASC
WITH
    id, doi, version, source, journal, title, abstract, pub_date, auth, ORCID, nb_figures,
    {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process
RETURN DISTINCT 
    id, doi, version, source, journal, title, abstract, pub_date, 
    COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: ORCID}) AS authors,
    nb_figures, review_process
    ''',
    map={'doi': []},
    returns=['id', 'doi', 'version', 'source', 'journal', 'title', 'abstract', 'authors', 'pub_date', 'nb_figures', 'review_process']
)


BY_REVIEWING_SERVICE = Query(
  code='''
//MATCH (rev:Review)
//OPTIONAL MATCH (annot:PeerReviewMaterial)
//WITH COLLECT(DISTINCT rev.reviewed_by) + COLLECT(DISTINCT annot.reviewed_by) AS all_rev
//UNWIND all_rev AS reviewing
//WITH DISTINCT reviewing
UNWIND ['review commons', 'embo press', 'elife'] AS reviewing
MATCH (a:Article)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review {reviewed_by: reviewing})
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: reviewing})
WITH DISTINCT
    reviewing,
    a.doi AS doi,
    a.publication_date AS pub_date,
    review, annot
WHERE 
    EXISTS(review.text) OR EXISTS(annot.text)
WITH reviewing, doi, pub_date, review, annot
ORDER BY
    pub_date DESC
RETURN
    reviewing AS name, 
    reviewing AS id,
    COLLECT(DISTINCT {doi: doi, info: {}, pub_date: pub_date}) AS papers
  ''',
  returns=['name', 'id', 'papers']
)

FIG_BY_DOI_IDX = Query(
    code='''
//fig by doi and index position
//
MATCH (a:Article {doi: $doi})-->(f:Fig {position_idx: toInteger($position_idx)})
RETURN
    a.doi AS doi,
    a.version AS version,
    a.title AS title,
    f.title AS fig_title,
    f.label AS fig_label,
    f.caption AS caption,
    f.position_idx AS fig_idx
ORDER BY version DESC, fig_idx ASC
    ''',
    map={'doi': ['doi', ''], 'position_idx': ['position_idx', '']},
    returns=['doi', 'version', 'title', 'fig_title', 'fig_label', 'caption', 'fig_idx']
)


PANEL_BY_NEO_ID = Query(
    code='''
MATCH (p:Panel)-->(ctCondTag)-->(h:H_Entity)
WHERE id(p) = $id
RETURN p.caption AS caption, COLLECT(DISTINCT h) AS tags
    ''',
    returns=['caption', 'tags'],
    map={'id': []}
)


REVIEW_PROCESS_BY_DOI = Query(
  code='''
MATCH (a:Article {doi: $doi})-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH a, review, response, annot
ORDER BY review.review_idx ASC
RETURN a.doi as doi, {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process
  ''',
  map={'doi': []},
  returns=['doi', 'review_process']
)


BY_METHOD = Query(
    code='''
//pre listed methods
UNWIND [
  {name: 'electron microscopy',   regex: '.*electron micro.*'            },
  {name: 'flow cytometry',        regex: '.*electron micro.*'            },
  {name: 'crystal structures',    regex: '.*(crystallo|crystal struct).*'},
  {name: 'immunoprecipitation',   regex: '.*immunoprecip.*'              },
  {name: 'immunohistochemistry', regex: '.*immunohistoc.*'               },
  {name: 'histology',             regex: '.*histol.*'                    },
  {name: 'pseudotype entry',      regex: '.*pseudotype.*'                }
] AS query
MATCH (q:Term)<-[:Has_text]-(h:H_Entity {category: "assay"})
WHERE 
  q.text =~ query.regex
  OR
  h.name =~ query.regex
WITH h, query.name AS name
MATCH (h)-[:Has_text]->(syn1:Term)
OPTIONAL MATCH
   (h)-[:Has_text]->(:Term)<--(bridge:H_Entity {category: "assay"})-->(syn2:Term)
WITH name, COLLECT (DISTINCT syn1.text) + [h.name, bridge.name]  as all_synonyms //COLLECT(syn2.text) + [bridge.name] 
UNWIND all_synonyms AS syn
WITH DISTINCT syn, name
WHERE NOT syn IS NULL
WITH syn, name
MATCH (a:SDArticle {journalName:'biorxiv'})-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag {category: "assay"})-->(h:H_Entity)-[:Has_text]->(te:Term {text: syn})
WITH DISTINCT
  name, {doi: a.doi, info: COLLECT(DISTINCT {id: id(p), title: f.fig_label, text: p.caption}), pub_date: a.pub_date} AS paper
ORDER BY paper.pub_date DESC
RETURN DISTINCT
   name AS name, name AS id, COLLECT(paper) AS papers
    ''',
    returns=['name', 'id', 'papers']
)


BY_HYP = Query(
    code='''
//Exclusion list based on SourceData normalized entities
MATCH (syn:Term)<--(entity:H_Entity)<--(ct:CondTag)
WHERE 
  entity.ext_ids <> ""
WITH DISTINCT entity.name AS name, COLLECT(DISTINCT syn.text) AS synonyms, COLLECT(DISTINCT ct) AS cts, 1.0*COUNT(DISTINCT ct) AS N
UNWIND cts as ct
WITH DISTINCT name, synonyms, N, ct.role as role, 1.0*COUNT(DISTINCT ct) AS N_role
WITH name, synonyms, role, N, N_role, 100.0*(N_role / N) AS fract
ORDER BY N DESC, fract DESC
WITH name, synonyms, N, COLLECT(role)[0] AS dominant_role, COLLECT(fract)[0] AS dom_fract
WHERE 
  (dominant_role = "normalizing" OR dominant_role = "reporter" OR dominant_role = "component")
  AND
  dom_fract > 75 AND N > 10.0
WITH COLLECT(name) + synonyms AS all
UNWIND all as terms
WITH COLLECT(DISTINCT terms) AS exclusion_list

//prioritize manually curated papers
MATCH (a:SDArticle)
WHERE toLower(a.journalName) IN ["biorxiv", "medrxiv"]
WITH a, exclusion_list
ORDER BY a.source DESC // manually curated source = 'sdapi' sorted before automatic papers where source = 'eebapi'
WITH DISTINCT a.doi AS doi, COLLECT(a) AS same_paper, exclusion_list
WITH same_paper[0] as a, exclusion_list

MATCH
  (a)-->(f:SDFigure)-->(p:SDPanel),
  path_1=(p)-->(i:CondTag {role: "intervention"})-->(ctrl:H_Entity)-->(ctrl_term:Term),
  path_2=(p)-->(m:CondTag {role: "assayed"})-->(meas:H_Entity)-->(meas_term:Term)
WHERE
  ctrl.name <> meas.name // could still be 2 entities normalized differently
  AND
  NONE (n IN nodes(path_1) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
  AND
  NONE (n IN nodes(path_2) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
WITH DISTINCT
    a, f, p, 
    ctrl.name AS ctrl_name, 
    meas.name AS meas_name
ORDER BY f.fig_label ASC, p.panel_label ASC
WITH DISTINCT
    a, 
    COLLECT(DISTINCT p{.*, id: id(p), title: f.fig_labell}) AS panels,
    COUNT(DISTINCT p) AS N_panels,
    ctrl_name, meas_name
ORDER BY ctrl_name, meas_name //deterministic order
WITH a, panels, N_panels, COLLECT(DISTINCT ctrl_name) AS ctrl_v, COLLECT(DISTINCT meas_name) AS meas_v
WHERE N_panels > 1
WITH 
  a, 
  [p IN panels | {id: p.id, label: p.panel_label, title: p.title, text: p.caption}] AS panel_captions,
  N_panels, 
  ctrl_v, meas_v
MATCH (a)-->(:SDFigure)-->(:SDPanel)-->(:CondTag)-->(assay:H_Entity {category: "assay"})
WITH DISTINCT a, panel_captions, N_panels, {ctrl_v: ctrl_v, meas_v: meas_v} AS hyp, COUNT(DISTINCT assay) AS N_assay
ORDER BY N_panels DESC, a.pub_date DESC
WITH a, COLLECT(panel_captions)[0] AS panels, COLLECT(hyp)[0] AS dominant, N_assay
WHERE N_assay > 3
WITH a, panels, dominant, N_assay
LIMIT 20
WITH dominant, COLLECT({doi: a.doi, info: panels, pub_date: a.pub_date}) AS papers
WITH COLLECT([dominant, papers]) AS all_results
UNWIND range(0, size(all_results)-1) as i
RETURN i as id, all_results[i][0] AS hyp, all_results[i][1] AS papers
    ''',
    returns=['id', 'hyp', 'papers']
)


BY_MOLECULE = Query(
    code='''
//Exclusion list based on SourceData normalized entities
MATCH (syn:Term)<--(mol:H_Entity)<--(ct:CondTag)
WHERE 
  mol.type = "small_molecule" OR mol.type = "molecule"
  AND 
  mol.ext_ids <> ""
WITH DISTINCT mol.name AS name, COLLECT(DISTINCT syn.text) AS synonyms, COLLECT(DISTINCT ct) AS cts, 1.0*COUNT(DISTINCT ct) AS N
UNWIND cts as ct
WITH DISTINCT name, synonyms, N, ct.role as role, 1.0*COUNT(DISTINCT ct) AS N_role
WITH name, synonyms, role, N, N_role, 100.0*(N_role / N) AS fract
ORDER BY N DESC, fract DESC
WITH name, synonyms, N, COLLECT(role)[0] AS dominant_role, COLLECT(fract)[0] AS dom_fract
WHERE 
  (dominant_role = "normalizing" OR dominant_role = "reporter" OR dominant_role = "component")
  AND
  dom_fract > 75 AND N > 10.0
WITH COLLECT(name) + synonyms AS all
UNWIND all as terms
WITH COLLECT(DISTINCT terms) AS exclusion_list

//
MATCH
  (query:H_Entity {category: "entity"})-[:Has_text]->(syn1:Term)
WHERE 
  (query.type = "molecule" OR query.type = "small_molecule")
  //exclude known artefacts...
  AND
  (NOT syn1.text = "a" OR syn1.text = "-")
  AND 
  (NOT syn1.text IN exclusion_list)
OPTIONAL MATCH
  (query:H_Entity {category: "entity"})-[:Has_text]->(:Term)<-[:Has_text]-(secondary:H_Entity {category: "entity"})-[:Has_text]->(syn2:Term)
WHERE 
  (query.type = "molecule" OR query.type = "small_molecule")
  AND
  (secondary.type = "molecule" OR secondary.type = "small_molecule")
  AND 
  (NOT syn2.text IN exclusion_list)
WITH DISTINCT [query, secondary] AS queries, syn1, syn2
UNWIND queries AS query
WITH DISTINCT query, syn1, syn2
WHERE NOT query is NULL
WITH DISTINCT query,  [query.name] + COLLECT(syn1.text) + COLLECT(syn2.text) AS all_synonyms
UNWIND all_synonyms AS syn
WITH DISTINCT query, syn
ORDER BY syn
WITH DISTINCT query, COLLECT(DISTINCT syn) AS synonym_sets
ORDER BY size(query.name) DESC
WITH DISTINCT COLLECT(DISTINCT query) AS query_group, synonym_sets
UNWIND synonym_sets AS synonym
WITH query_group, synonym

MATCH
  (paper:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(mol:H_Entity {category: "entity"})-[:Has_text]->(mol_name:Term {text: synonym})
WHERE
  toLower(paper.journalName) IN ["biorxiv", "medrxiv"]
  AND
  (mol.type = "molecule" OR mol.type = "small_molecule")
  AND
  datetime(paper.pub_date) > datetime('2020-04-01')
WITH DISTINCT query_group, paper, f, p, synonym
ORDER BY f.fig_label ASC
WITH DISTINCT query_group, paper, COLLECT(DISTINCT {id: id(p), title: f.fig_label, text: p.caption}) AS panels, COUNT(DISTINCT p) AS N_panels, COLLECT(DISTINCT synonym) AS synonyms_in_paper
WHERE 
  N_panels > 2
WITH DISTINCT
  query_group,
  COLLECT(DISTINCT {doi: paper.doi, title:paper.title, syn: synonyms_in_paper, info: panels, pub_date: paper.pub_date}) AS papers,
  COUNT(DISTINCT paper) AS N_papers
ORDER BY N_papers DESC
LIMIT 20
WITH
  query_group[0].name AS molecule, papers
RETURN
  molecule AS name, molecule as id, papers
''',
    returns=['name', 'id', 'papers']
)


AUTOMAGIC = Query(
    code='''
// rank sum

///////////////////////PART A: RANK BY NUMBER OF ASSAYS///////////////////////////////

//start with only most recent version
//MATCH (preprint:SDArticle {journalName: "biorxiv"})
//WITH preprint
//ORDER BY preprint.version DESC
//WITH DISTINCT preprint.doi AS doi, COLLECT(DISTINCT preprint)[0] AS a //keep only the most recent

// find entities
MATCH (a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "assay"})-[:Has_text]->(name:Term)
WITH
  a, entity, name
//find synonyms
MATCH
   (name)<-[:Has_text]-(:H_Entity {category:"assay"})-[:Has_text]->(syn1:Term)
//combine synonyms
WITH DISTINCT a, entity, COLLECT(name) + COLLECT(syn1) AS all_synonyms
UNWIND all_synonyms AS syn_term
// remove duplicates
WITH DISTINCT a, entity, syn_term.text AS syn
// impose deterministic order
ORDER BY syn
WITH DISTINCT a, entity, COLLECT(DISTINCT syn) AS synonyms
ORDER BY id(entity)
//collapse identical synonym groups
WITH DISTINCT a, COLLECT(DISTINCT entity) AS entity_group, synonyms
WITH DISTINCT a, COLLECT(DISTINCT entity_group) AS entity_groups, COUNT(DISTINCT entity_group) AS N_entities, COLLECT(DISTINCT synonyms) AS synonym_groups
ORDER BY N_entities DESC
WITH COLLECT(DISTINCT {title: a.title, doi: a.doi, source:a.source, info: synonym_groups, pub_date: a.pub_date, N_entities: N_entities}) as preprint_list
WITH preprint_list, range(1, size(preprint_list)) AS ranks
UNWIND ranks as i
WITH COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_assay

///////////////////////PART B: RANK BY NUMBER OF ENTITIES///////////////////////////////

//start with only most recent version
MATCH (preprint:SDArticle {journalName: "biorxiv"})
WITH preprint, ranked_by_assay
ORDER BY preprint.version DESC
WITH DISTINCT preprint.doi AS doi, COLLECT(DISTINCT preprint)[0] AS a, ranked_by_assay //keep only the most recent

// find entities
MATCH (a)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "entity"})-[:Has_text]->(name:Term)
WITH
  a, entity, name, ranked_by_assay
//find synonyms
MATCH
   (name)<-[:Has_text]-(s:H_Entity {category:"entity"})-[:Has_text]->(syn1:Term)
WHERE s.type = entity.type
//combine synonyms
WITH DISTINCT a, entity, COLLECT(name) + COLLECT(syn1) AS all_synonyms, ranked_by_assay
UNWIND all_synonyms AS syn_term
// remove duplicates
WITH DISTINCT a, entity, syn_term.text AS syn, ranked_by_assay
// impose deterministic order
ORDER BY syn
WITH DISTINCT a, entity, COLLECT(DISTINCT syn) AS synonyms, ranked_by_assay
ORDER BY id(entity)
//collapse identical synonym groups
WITH DISTINCT a, COLLECT(DISTINCT entity) AS entity_group, synonyms, ranked_by_assay
WITH DISTINCT a, COLLECT(DISTINCT entity_group) AS entity_groups, COUNT(DISTINCT entity_group) AS N_entities, COLLECT(DISTINCT synonyms) AS synonym_groups, ranked_by_assay
ORDER BY N_entities DESC
WITH COLLECT(DISTINCT {title: a.title, doi: a.doi, source:a.source, info: synonym_groups, pub_date: a.pub_date, N_entities: N_entities}) as preprint_list, ranked_by_assay
WITH preprint_list, range(1, size(preprint_list)) AS ranks, ranked_by_assay
UNWIND ranks as i
WITH COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_entities, ranked_by_assay


///////////////////////PART C: RETURN BY SUM OF RANKS///////////////////////////////
//sum of ranks
WHERE (ranked_by_entities <> []) AND (ranked_by_assay <> [])
WITH ranked_by_entities + ranked_by_assay AS ranked
UNWIND ranked as item
WITH DISTINCT {doi: item.preprint.doi, info: COLLECT(DISTINCT {text: item.preprint.info, pub_date: item.preprint.pub_date}), rank: SUM(item.rank)} as paper, COLLECT(item.rank) AS ranks
WHERE size(ranks)=2
WITH paper, ranks
ORDER BY paper.rank ASC
LIMIT 10
RETURN 'automagic list' AS name, "1" AS id, COLLECT(paper) AS papers
    ''',
    returns=['name', 'id', 'papers']
)


LUCENE_SEARCH = Query(
    code='''
// Full-text search on multiple indices.

//CALL db.index.fulltext.createNodeIndex("title", ["SDArticle"], ["title"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("title", query) YIELD node, score
WITH
  node.doi AS doi, node.title AS text, score, "title" AS source, query
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score, source, query

UNION

//CALL db.index.fulltext.createNodeIndex("abstract",["SDArticle"], ["abstract"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("abstract", query) YIELD node, score
WITH
  node.doi AS doi, node.title as text, score, "abstract" as source, query
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score, source, query
LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("caption",["SDPanel"], ["caption"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("caption", query) YIELD node, score
MATCH (article:SDArticle)-[:has_figure]->(f:SDFigure)-[:has_panel]->(node)
WITH DISTINCT
  article.doi as doi, node.caption as text, score, "caption" AS source, query
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score, source, query
LIMIT 20

//UNION

//slow!
//CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"]);
//CALL db.index.fulltext.queryNodes("entity_name", $query) YIELD node, score
//MATCH (sd_article:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(ct:CondTag)-[:Identified_by]->(h:H_Entity)
//WHERE h.name = node.name AND node.name <> ""
//WITH DISTINCT 
//  sd_article.doi as doi, h.name as text, score, "entity" as source, query
//ORDER BY score DESC
//RETURN 
//  doi, [{text: text}] AS info, score, source, query
//LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname", "given_names"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("name", query) YIELD node, score
MATCH (article:SDArticle)-->(author:Contrib)
WHERE author.surname = node.surname AND author.given_names = node.given_names
WITH DISTINCT 
  article.doi as doi, node.surname as text, score, "author" AS source, query
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score, source, query
LIMIT 20
''',
    map={'query': ['query', '']},
    returns=['doi', 'info', 'score', 'source', 'query']
)

SEARCH_DOI = Query(
  code='''
WITH $query AS query
MATCH (article:SDArticle)
WHERE article.doi = query
RETURN
  article.doi AS doi, [{text: article.doi}] AS info, 10.0 AS score, 'doi' AS source, query
  ''',
  map={'query': ['query', '']},
  returns=['doi', 'info', 'score', 'source', 'query']
)

STATS = Query(
    code='''
MATCH (a:Article)
WITH COUNT(a) AS N_jats
MATCH (sd:SDPanel {source: 'sdapi'})
WITH COUNT(sd) AS N_sdapi, N_jats
MATCH (eeb:SDArticle {source: 'eebapi'})
WITH COUNT(eeb) AS N_eeb, N_sdapi, N_jats
MATCH (n)
WITH COUNT(n) AS N_nodes, N_eeb, N_sdapi, N_jats
MATCH ()-[r]->()
RETURN COUNT(r) AS N_rel, N_nodes, N_eeb, N_sdapi, N_jats
    ''',
    returns=['N_jats', 'N_sdapi', 'N_eeb', 'N_nodes', 'N_rel']
)


PANEL_SUMMARY = Query(
    code='''
// panel summary
// Thi query provides a simplified summary of a panel.
// Entities are listed in a simplified way for display.
// Each entity has a primary label (i.e. the name of the entity),
// a secondary label providing complementary info depending on entity type,
// and a url pointing to an external knowledge base
//
// Args:
//    panel_id: the panel id
// Returns
//    fig_label: the label of the parent figure
//    fig_title: the title of the parent figure
//    panel_label: the lable of the panel
//    caption: the caption of the panel
//    controlled_var: a list of entities linked to the controlled variable(s) of the experiment
//    measured_var: a list of entities linked to the measured variable(s) of the experiment
//    other: a list of other entities involved in the experiment
//    methods: the experimental observation and measurement assays
MATCH
    (a:SDArticle)-->(f:SDFigure)-->(p:SDPanel {panel_id: $panel_id})
WITH
    a.doi AS doi,
    f.fig_label AS fig_label,
    p
// find the matching figures from jats to extract the figure title
MATCH
    (ax:Article {doi:doi})-->(fx:Fig {label: fig_label})
WITH 
    doi,
    fig_label,
    fx.title as fig_title,
    p.panel_label as panel_label,
    p.caption as caption,
    p
// find the entities linked to the target panel
MATCH
    (p)-->(ct:CondTag), (resolver:Resolver)
WHERE
    ct.role <> "reporter" AND ct.role <>"normalizing" AND
    ct.ext_dbs = resolver.name
WITH
    doi,
    fig_label,
    fig_title,
    panel_label,
    caption,
    ct,
    resolver
// find the corresponding entities in the full paper to make a statistic for ranking
MATCH
    (a:SDArticle {doi: doi})-->(:SDFigure)--> (all_panels:SDPanel)-->(other_ct:CondTag {text:ct.text})
WITH DISTINCT
    doi,
    fig_label,
    fig_title,
    panel_label,
    caption,
    ct,
    resolver,
    COUNT(DISTINCT other_ct) AS freq
// combine entities with frequency into single list that can be processed
WITH 
    fig_label,
    fig_title,
    panel_label,
    caption,
    COLLECT(DISTINCT {
        text: ct.text,
        ext_ids: ct.ext_ids, 
        role: ct.role,
        type: ct.type,
        category: ct.category, 
        freq: freq, 
        ext_tax_names: ct.ext_tax_names,
        href: resolver.url + ct.ext_ids
    }) AS entities
// sort and aggregate depending on role
WITH
    [e IN entities WHERE (e['role']='intervention' OR e['role']='experiment') | e] AS controlled_entities,
    [e IN entities WHERE e['role']='assayed' | e] AS measured_entities,
    [e IN entities WHERE e['category']='assay' | e] AS assays,
    [e IN entities WHERE (e['type']='component' OR e['category']='disease') | e] AS other_entities,
    fig_label, fig_title, panel_label, caption
// standardize the format of the output
RETURN
    [e in controlled_entities | {primary_label: e.text, secondary_label: e.ext_tax_names, href: e.href}] as controlled_var,
    [e IN measured_entities WHERE e['role']='assayed' | {primary_label:e.text, secondary_label: e.ext_tax_names, href: e.href}] AS measured_var,
    [e IN assays WHERE e['category']='assay' | {primary_label: e.text, secondary_label: "", href: e.href}] AS methods,
    [e IN other_entities WHERE (e['type']='component' OR e['category']='disease') | {primary_label: e.text, secondary_label: e.ext_tax_names, href: e.href}] AS other,
    fig_label, fig_title, panel_label, caption
    ''',
    map={'panel_id': []},
    returns=['fig_label', 'fig_title', 'panel_label', 'caption', 'controlled_var', 'measured_var', 'other', 'methods']
)



POPULAR_METHODS = Query(
    code='''
// find most popular method with synonym aggregation
MATCH (a:SDArticle {journalName:'biorxiv'})-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag {category: "assay"})-->(h:H_Entity)
WITH DISTINCT a, ct, h
ORDER BY a.pub_date DESC
WITH DISTINCT
    COUNT(DISTINCT a) AS popularity,
    COLLECT(DISTINCT a.doi)[..10] AS top10,
    h
ORDER BY popularity DESC
MATCH (h)-->(t:Term)<--(h2:H_Entity)<--(ct:CondTag)<--(p:SDPanel)<--(f:SDFigure)<--(a:SDArticle)
WITH DISTINCT
    h, top10,
    h2,
    COUNT(DISTINCT a) AS N
ORDER BY N DESC
WITH DISTINCT
    h.name AS synonym,
    top10,
    COLLECT(DISTINCT h2.name)[0] AS method
UNWIND top10 AS paper
WITH
    synonym,
    paper,
    method
RETURN
    COLLECT(DISTINCT synonym) AS synonyms,
    COLLECT(DISTINCT paper) AS papers,
    method
LIMIT 25
    ''',
    returns=['method', 'popularity']
)





OLDER_BY_HYP = Query(
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
