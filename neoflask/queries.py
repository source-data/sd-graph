from neotools.db import Query


class COVID19(Query):

    code = '''
WITH
    "2019-nCoV OR 2019nCoV OR COVID-19 OR SARS-CoV-2 OR SARS-CoV2 OR SAR-CoV2 OR SRAS-CoV-2" AS search_query
// CALL db.index.fulltext.createNodeIndex("abstract_jats", ["Article"], ["abstract"], {analyzer: "english"});
CALL db.index.fulltext.queryNodes("title_jats", search_query) YIELD node, score
WITH node.doi AS doi, node.version AS version, node, score
ORDER BY score DESC, version DESC
WITH DISTINCT doi, COLLECT(node) AS versions, COLLECT(score) AS scores
WHERE scores[0] > 0.02
WITH doi, versions[0] AS most_recent, scores[0] AS score
MATCH (a:Article {doi:doi, version: most_recent.version})-->(f:Fig)
WITH COLLECT(DISTINCT doi) AS from_title

WITH
    "2019-nCoV OR 2019nCoV OR COVID-19 OR SARS-CoV-2 OR SARS-CoV2 OR SAR-CoV2 OR SRAS-CoV-2" AS search_query,
    from_title
    CALL db.index.fulltext.queryNodes("abstract_jats", search_query) YIELD node, score
WITH node.doi AS doi, node.version AS version, node, score,
 from_title
ORDER BY score DESC, version DESC
WITH DISTINCT doi, COLLECT(node) AS versions, COLLECT(score) AS scores,
  from_title
WHERE scores[0] > 0.01
WITH doi, versions[0] AS most_recent, scores[0] AS score,
  from_title
MATCH (a:Article {doi:doi, version: most_recent.version})-->(f:Fig)
WITH COLLECT(DISTINCT a{.*, score: score}) AS from_abstract, from_title
UNWIND from_abstract AS a
WITH a
WHERE a.doi IN from_title
RETURN
    a.doi AS id,
    a.publication_date AS pub_date,
    a.title AS title,
    a.abstract AS abstract,
    a.version AS version,
    a.doi AS doi,
    a.journal_title AS journal,
    a.score AS score
ORDER BY DATETIME(pub_date) DESC, score DESC
    '''
    map = {}
    returns = ['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'score']


class REFEREED_PREPRINTS(Query):

    code = '''
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
    '''
    returns = ['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'nb_figures', 'review_process']


class BY_DOI(Query):

    code = '''
//by doi
//
MATCH (preprint:Article {doi: $doi})
WITH preprint, preprint.version AS version
ORDER BY version DESC
WITH COLLECT(preprint)[0] AS a
OPTIONAL MATCH
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
    a.journal_title AS journal, // this is the preprint server
    a.title AS title,
    a.abstract AS abstract,
    a.journal_doi AS journal_doi,
    a.published_journal_title AS published_journal_title, // this is the journal of final publication
    toString(DATETIME(a.publication_date)) AS pub_date, // pub date as preprint!
    auth,
    id.text AS ORCID,
    COUNT(DISTINCT f) AS nb_figures,
    review, response, annot
WITH id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title, auth, ORCID, nb_figures, review, response, annot
ORDER BY
    review.review_idx ASC,
    auth.position_idx ASC
WITH
    id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title, auth, ORCID, nb_figures,
    {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process
RETURN DISTINCT 
    id, doi, version, source, journal, title, abstract, toString(DATETIME(pub_date)) AS pub_date, //standardization of date time format, necessary for Safari
    journal_doi, published_journal_title, COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: ORCID}) AS authors,
    nb_figures, review_process
    '''
    map = {'doi': []}
    returns = ['id', 'doi', 'version', 'source', 'journal', 'title', 'abstract', 'authors', 'pub_date', 'journal_doi', 'published_journal_title', 'nb_figures', 'review_process']


class FIG_BY_DOI_IDX(Query):

    code = '''
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
    '''
    map = {'doi': ['doi', ''], 'position_idx': ['position_idx', '']}
    returns = ['doi', 'version', 'title', 'fig_title', 'fig_label', 'caption', 'fig_idx']


class PANEL_BY_NEO_ID(Query):

    code = '''
MATCH (p:Panel)-->(ctCondTag)-->(h:H_Entity)
WHERE id(p) = $id
RETURN p.caption AS caption, COLLECT(DISTINCT h) AS tags
    '''
    returns = ['caption', 'tags']
    map = {'id': []}


class REVIEW_PROCESS_BY_DOI(Query):

    code = '''
MATCH (a:Article {doi: $doi})-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH a, review, response, annot
ORDER BY review.review_idx ASC
RETURN a.doi as doi, {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process
  '''
    map = {'doi': []}
    returns = ['doi', 'review_process']


class BY_REVIEWING_SERVICE(Query):

    code = '''
// Using precomputed Viz nodes
MATCH (paper:VizPaper {query: "by_reviewing_service"})
WHERE DATETIME(paper.peer_review_date) > DATETIME($limit_date)
OPTIONAL MATCH (paper)-[:HasInfo]->(info:VizInfo)
WITH DISTINCT
   paper, info,
   {title: info.title, text: info.text, rank: info.rank, entities: []} AS info_card
ORDER BY
    DATETIME(paper.rank) ASC, // rank is pub_date
    info.rank ASC // rank is figure label
WITH DISTINCT
    paper, COLLECT(info_card) AS info_cards
RETURN
    paper.id AS id,
    paper.id AS name,
    COLLECT(DISTINCT {doi: paper.doi, info: info_cards, pub_date: paper.pub_date, peer_review_date: toString(paper.peer_review_date)}) AS papers
  '''
    map = {'limit_date': []}
    returns = ['name', 'id', 'papers']


class BY_HYP(Query):

    code = '''
// Using precomputed Viz nodes
MATCH 
  (paper:VizPaper {query: "by_hyp"})-->(info:VizInfo),
  (paper)-[:HasEntity]->(ctrl_v:VizEntity)-[:HasPotentialEffectOn]->(meas_v:VizEntity)
WHERE DATETIME(paper.pub_date) > DATETIME($limit_date)
OPTIONAL MATCH
  (info)-[:HasEntity]->(entity:VizEntity)
WITH DISTINCT paper, info, ctrl_v, meas_v, entity
ORDER BY
  id(ctrl_v) ASC, // deterministic
  id(meas_v) ASC, // deterministic
  entity.category DESC, entity.role DESC // to male viz nicer, but frontend may have to fine tune
WITH DISTINCT
  paper, info,
  COLLECT(DISTINCT entity{.*}) AS panel_entities,
  {ctrl_v: COLLECT(DISTINCT ctrl_v.text), meas_v: COLLECT(DISTINCT meas_v.text)} AS hyp
ORDER BY
   DATETIME(paper.rank) DESC, // rank is pub date
   info.rank ASC // rank is fig label + panel label
WITH
  paper, hyp,
  info{
    .*, // title (label of the figure), text (caption of the figure), rank, id 
    entities: panel_entities // entity properties: text, category, type role, ext_id
   } as extended_info
WITH
  paper, COLLECT(extended_info) as info_cards, hyp
WITH DISTINCT
  hyp,
  COLLECT({doi: paper.doi, info: info_cards, pub_date: paper.pub_date}) AS papers
WITH COLLECT([hyp, papers]) AS all_results
UNWIND range(0, size(all_results)-1) as i
RETURN i as id, all_results[i][0] AS hyp, all_results[i][1] AS papers
    '''
    map = {'limit_date': []}
    returns = ['id', 'hyp', 'papers']


class AUTOMAGIC(Query):

    code = '''
// using precomputed Viz nodes
MATCH
  (paper:VizPaper {query: "automagic"}),
  (paper)-[:HasInfo]->(:VizInfo {title: 'Experimental approaches'})-[:HasEntity]->(exp_assays:VizEntity),
  (paper)-[:HasInfo]->(:VizInfo {title: 'Biological entities'})-[:HasEntity]->(biol_entities:VizEntity)
WHERE DATETIME(paper.pub_date) > DATETIME($limit_date)
WITH DISTINCT paper, exp_assays, biol_entities
ORDER BY
   paper.rank ASC //rank is rank sum score
WITH DISTINCT
  paper.doi AS doi, paper.pub_date AS pub_date, 
  [{title: "Experimental approaches", text: "", entities: COLLECT(DISTINCT {text: exp_assays.text})},
   {title: "Biological entities", text: "", entities: COLLECT(DISTINCT {text: biol_entities.text})}] AS info
WITH {doi: doi, info: info, pub_date: pub_date} AS paper
RETURN 'automagic list' AS name, "1" AS id, COLLECT(paper) AS papers
    '''
    map = {'limit_date': []}
    returns = ['name', 'id', 'papers']


class BY_METHOD(Query):
    code = '''
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
    '''
    returns = ['name', 'id', 'papers']


class BY_MOLECULE(Query):
    code = '''
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
'''
    returns = ['name', 'id', 'papers']


class LUCENE_SEARCH(Query):
    code = '''
// Full-text search on multiple indices.

//CALL db.index.fulltext.createNodeIndex("title", ["SDArticle"], ["title"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("title", query) YIELD node, score
WITH node, score, query
WHERE node.journalName = "biorxiv"
WITH
// weight 4x for results on title
  node.doi AS doi, node.title AS text, 1 * score AS weighted_score, "title" AS source, query
ORDER BY weighted_score DESC
RETURN 
// entities is obligatory field for info for compatibility with the other methods
  doi, [{title: "'" + $query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query

UNION

//CALL db.index.fulltext.createNodeIndex("abstract",["SDArticle"], ["abstract"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("abstract", query) YIELD node, score
WITH node, score, query
WHERE node.journalName = "biorxiv"
WITH
// weight 2x for results on abstract
  node.doi AS doi, node.title as text, 1 * score AS weighted_score, "abstract" as source, query
ORDER BY weighted_score DESC
RETURN 
  doi, [{title: "'" + $query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("caption",["SDPanel"], ["caption"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("caption", query) YIELD node, score
MATCH (article:SDArticle {journalName: "biorxiv"})-[:has_figure]->(f:SDFigure)-[:has_panel]->(node)
WITH DISTINCT
// weight 1 for caption
  article.doi as doi, node.caption as text, 1 * score AS weighted_score, "caption" AS source, query
ORDER BY weighted_score DESC
RETURN 
  doi, [{title: "'" + $query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
LIMIT 20

//UNION

//slow!
//CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"]);
//CALL db.index.fulltext.queryNodes("entity_name", $query) YIELD node, score
//MATCH (sd_article:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(ct:CondTag)-[:Identified_by]->(h:H_Entity)
//WHERE h.name = node.name AND node.name <> ""
//WITH DISTINCT 
//  sd_article.doi as doi, h.name as text, 1.0 * score AS weighted_score, "entity" as source, query
//ORDER BY score DESC
//RETURN 
//  doi, [{title: "'" + $query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
//LIMIT 20

UNION

//CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname", "given_names"]);
WITH $query AS query
CALL db.index.fulltext.queryNodes("name", query) YIELD node, score
MATCH (article:SDArticle {journalName: "biorxiv"})-->(author:Contrib)
WHERE author.surname = node.surname AND author.given_names = node.given_names
WITH DISTINCT
//weight 4x for results on authors
  article.doi as doi, node.surname as text, 1 * score AS weighted_score, "author list" AS source, query
ORDER BY weighted_score DESC
RETURN 
  doi, [{title: $query + " found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
LIMIT 20
'''
    map = {'query': []}
    returns = ['doi', 'info', 'score', 'source', 'query']


class SEARCH_DOI(Query):
  code = '''
WITH $query AS query
MATCH (article:SDArticle)
WHERE article.doi = query
RETURN
  article.doi AS doi, [{title: 'doi match', text: article.doi, entities:[]}] AS info, 10.0 AS score, 'doi' AS source, query
  '''
  map = {'query': []}
  returns = ['doi', 'info', 'score', 'source', 'query']


class STATS(Query):
    code = '''
MATCH (a:Article)
WITH COUNT(a) AS N_jats
MATCH (sd:SDPanel {source: 'sdapi'})
WITH COUNT(sd) AS N_sdapi, N_jats
OPTIONAL MATCH (eeb:SDArticle {source: 'eebapi'})
WITH COUNT(eeb) AS N_eeb, N_sdapi, N_jats
MATCH (n)
WITH COUNT(n) AS N_nodes, N_eeb, N_sdapi, N_jats
MATCH ()-[r]->()
RETURN COUNT(r) AS N_rel, N_nodes, N_eeb, N_sdapi, N_jats
    '''
    returns = ['N_jats', 'N_sdapi', 'N_eeb', 'N_nodes', 'N_rel']


class PANEL_SUMMARY(Query):
    code = '''
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
    '''
    map = {'panel_id': []},
    returns = ['fig_label', 'fig_title', 'panel_label', 'caption', 'controlled_var', 'measured_var', 'other', 'methods']


class POPULAR_METHODS(Query):
    code = '''
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
    '''
    returns = ['method', 'popularity']
