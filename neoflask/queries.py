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
    COUNT(f) AS nb_figures,
    score
ORDER BY pub_date DESC, score DESC;
    ''',
    map={},
    returns=['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'nb_figures', 'score']
)

BY_DOI = Query(
    code='''
//by doi
//
MATCH (a:Article {doi: $doi})-->(author:Contrib)
OPTIONAL MATCH (author)-->(id:Contrib_id)
OPTIONAL MATCH (a)-->(f:Fig)
WITH
    id(a) AS id,
    a.doi AS doi,
    a.version AS version,
    'biorxiv' AS journal,
    a.title AS title,
    a.abstract AS abstract,
    a.publication_date AS pub_date,
    author.surname AS surname,
    author.given_names AS given_name,
    author.position_idx AS author_rank,
    author.corresp = "yes" AS corr_author,
    COUNT(f) AS nb_figures,
    id.text AS ORCID
ORDER BY version DESC, author_rank DESC
RETURN id, doi, version, journal, title, abstract, COLLECT([surname, given_name, ORCID, corr_author]) AS authors, pub_date, nb_figures

    ''',
    map={'doi': []},
    returns=['id', 'doi', 'version', 'journal', 'title', 'abstract', 'authors', 'pub_date', 'nb_figures']
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

BY_METHOD = Query(
    code='''
//pre listed methods
UNWIND ['flow cytometry', 'electron microscope', 'immunoprecipitation', 'confocal microscopy', 'immunohistochemistry', 'histology', 'pseudovirus cell entry'] AS query
MATCH (q:Term {text: query})<-[:Has_text]-(h:H_Entity {category: "assay"})-[:Has_text]->(syn:Term)
WITH q, syn
MATCH (a:SDArticle {journalName:'biorxiv'})-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag {category: "assay"})-->(h:H_Entity)-[:Has_text]->(syn)
WITH DISTINCT
   q, {doi: a.doi, info: COLLECT(DISTINCT {id: id(p), text: p.caption}), pub_date: a.pub_date} AS paper
ORDER BY paper.pub_date DESC
RETURN DISTINCT
   q.text AS name, q.text AS id, COLLECT(paper) AS papers
    ''',
    returns=['name', 'id', 'papers']
)


BY_HYP = Query(
    code='''
MATCH
    (a:SDArticle {journalName: "biorxiv"})-->(f:SDFigure)-->(p:SDPanel),
    (p)-->(i:CondTag {role: "intervention"})-->(ctrl_v:H_Entity),
    (p)-->(m:CondTag {role: "assayed"})-->(meas_v:H_Entity)
WHERE
    ctrl_v.name <> meas_v.name // could still be 2 entities normalized differently
WITH DISTINCT
    a,
    COLLECT(DISTINCT p) AS panels,
    COUNT(DISTINCT p) AS N_panels,
    ctrl_v,
    meas_v
WHERE N_panels > 2
WITH DISTINCT a, {ctrl_v: ctrl_v.name, meas_v: meas_v.name} AS hyp, [p IN panels | {id: id(p), text: p.caption}] AS panel_captions, N_panels
ORDER BY N_panels DESC
WITH a, COLLECT(hyp)[0] AS dominant, COLLECT(panel_captions)[0] AS panels
ORDER BY a.pub_date DESC
WITH dominant, COLLECT({doi: a.doi, info: panels}) AS papers
WITH COLLECT([dominant, papers]) AS all_results
UNWIND range(0, size(all_results)-1) as i
RETURN i as id, all_results[i][0] AS hyp, all_results[i][1] AS papers
    ''',
    returns=['id', 'hyp', 'papers']
)


BY_MOLECULE = Query(
    code='''
MATCH
  (query:H_Entity {category: "entity"})-[:Has_text]->(syn1:Term)
WHERE 
  query.type = "molecule" OR query.type = "small_molecule"
  //exclude known artefacts...
  AND
  (NOT syn1.text = "a" OR syn1.text = "-")
OPTIONAL MATCH
  (query:H_Entity {category: "entity"})-[:Has_text]->(mol_name:Term)<-[:Has_text]-(secondary:H_Entity {category: "entity"})-[:Has_text]->(syn2:Term)
WHERE 
  (query.type = "molecule" OR query.type = "small_molecule")
  AND
  (secondary.type = "molecule" OR secondary.type = "small_molecule")
WITH DISTINCT query, COLLECT(syn1) + COLLECT(syn2) AS all_synonyms
UNWIND
   all_synonyms AS syn_term
WITH DISTINCT query, syn_term.text as syn
ORDER BY syn
WITH DISTINCT query, COLLECT(DISTINCT syn) AS synonym_sets
WITH DISTINCT COLLECT(DISTINCT query) AS query_group, synonym_sets
UNWIND synonym_sets AS synonym
MATCH
  (paper:SDArticle {journalName:'biorxiv'})-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(mol:H_Entity {category: "entity"})-[:Has_text]->(mol_name:Term {text: synonym})
WHERE
  mol.type = "molecule" OR mol.type = "small_molecule"
WITH DISTINCT query_group, paper, COLLECT(DISTINCT {id: id(p), text: p.caption}) AS panels, COUNT(DISTINCT p) AS N_panels, COLLECT(DISTINCT synonym) AS synonyms_in_paper
WHERE N_panels > 1
WITH DISTINCT
  query_group,
  COLLECT(DISTINCT {doi: paper.doi, title:paper.title, syn: synonyms_in_paper, info: panels}) AS papers,
  COUNT(DISTINCT paper) AS N_papers
ORDER BY N_papers DESC
LIMIT 10
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
MATCH (preprint:SDArticle {journalName: "biorxiv"})
WITH preprint
ORDER BY preprint.version DESC
WITH DISTINCT preprint.doi AS doi, COLLECT(DISTINCT preprint)[0] AS a //keep only the most recent

// find entities
MATCH (a)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "assay"})-[:Has_text]->(name:Term)
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
WITH COLLECT(DISTINCT {title: a.title, doi: a.doi, info: synonym_groups, N_entities: N_entities}) as preprint_list
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
WITH COLLECT(DISTINCT {title: a.title, doi: a.doi, info: synonym_groups, N_entities: N_entities}) as preprint_list, ranked_by_assay
WITH preprint_list, range(1, size(preprint_list)) AS ranks, ranked_by_assay
UNWIND ranks as i
WITH COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_entities, ranked_by_assay


///////////////////////PART C: RETURN BY SUM OF RANKS///////////////////////////////
//sum of ranks
WHERE (ranked_by_entities <> []) AND (ranked_by_assay <> [])
WITH ranked_by_entities + ranked_by_assay AS ranked
UNWIND ranked as item
WITH DISTINCT {doi: item.preprint.doi, info: COLLECT(DISTINCT {text: item.preprint.info}), rank: SUM(item.rank)} as paper, COLLECT(item.rank) AS ranks
WHERE size(ranks)=2
WITH paper, ranks
ORDER BY paper.rank ASC
LIMIT 10
RETURN 'automagic list' AS name, "1" AS id, COLLECT(paper) AS papers
    ''',
    returns=['name', 'id', 'papers']
)


SEARCH = Query(
    code='''
// Full-text search on multiple indices.

//CALL db.index.fulltext.createNodeIndex("title", ["Article"], ["title"]);
CALL db.index.fulltext.queryNodes("title", $query) YIELD node, score
WITH 
  node.doi AS doi, node.title AS text, score, "title" AS source
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score
LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("abstract",["Article"], ["abstract"]);
CALL db.index.fulltext.queryNodes("abstract", $query) YIELD node, score
WITH
  node.doi AS doi, node.title as text, score, "abstract" as source
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score
LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("caption",["Fig"], ["caption"]);
CALL db.index.fulltext.queryNodes("caption", $query) YIELD node, score
MATCH (article:Article)-[:has_figure]->(node)
WITH DISTINCT
  article.doi as doi, node.caption as text, score, "caption" AS source
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score
LIMIT 20

//UNION

//slow!
//CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"]);
//CALL db.index.fulltext.queryNodes("entity_name", $query) YIELD node, score
//MATCH (sd_article:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(ct:CondTag)-[:Identified_by]->(h:H_Entity)
//WHERE h.name = node.name AND node.name <> ""
//WITH DISTINCT 
//  sd_article.doi as doi, h.name as text, score, "entity" as source
//ORDER BY score DESC
//RETURN 
//  doi, [{text: text}] AS info, score
//LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname"]);
CALL db.index.fulltext.queryNodes("name", $query) YIELD node, score
MATCH (article:Article)-->(author:Contrib)
WHERE author.surname = node.surname
WITH DISTINCT 
  article.doi as doi, node.surname as text, score, "author" AS source
ORDER BY score DESC
RETURN 
  doi, [{text: text}] AS info, score
LIMIT 20
''',
    map={'query': ['query', '']},
    returns=['doi', 'info', 'score']
)

STATS = Query(
    code='''
        MATCH (a:Article)
        WITH COUNT(a) AS total_preprints
        MATCH (sda:SDArticle {source: 'sdneo'}) 
        WITH COUNT(sda) AS AS covid19_preprints // wrong, placeholder, total_preprints
        MATCH (n) 
        WITH COUNT(n) AS total_nodes, total_preprints, covid19_preprints
        RETURN total_nodes, total_preprints, covid19_preprints
    ''',
    returns=['total_nodes', 'total_preprints', 'covid19_preprints']
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
