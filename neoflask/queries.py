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
// EXPLAIN MATCH (preprint:Article {doi: "10.1101/2020.04.19.049254"})
WITH preprint, preprint.version AS version
ORDER BY version DESC
WITH COLLECT(preprint)[0] AS a
OPTIONAL MATCH (a)-->(f:Fig)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
OPTIONAL MATCH (a)-->(auth:Contrib)
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
  COUNT(DISTINCT f) AS nb_figures,
  auth,
  review, response, annot
OPTIONAL MATCH (assay:VizEntity {category: 'assay'})<-[:HasEntity]-(:VizPaper {doi: doi})-[:HasEntity]->(entity:VizEntity {category: 'entity'})
OPTIONAL MATCH (auth)-->(auth_id:Contrib_id)
WITH
  id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title, 
  auth,
  auth_id.text AS ORCID, 
  nb_figures, review, response, annot,
  COLLECT(DISTINCT entity.text) AS entities, COLLECT(DISTINCT assay.text) AS assays
ORDER BY
    review.review_idx ASC,
    auth.position_idx ASC
WITH
    id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title, auth, ORCID, nb_figures,
    {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: annot {.*}} AS review_process,
    entities, assays
RETURN DISTINCT 
    id, doi, version, source, journal, title, abstract, toString(DATETIME(pub_date)) AS pub_date, //standardization of date time format, necessary for Safari
    journal_doi, published_journal_title, COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: ORCID}) AS authors,
    nb_figures, review_process,
    entities, assays
    '''
    map = {'doi': []}
    returns = ['id', 'doi', 'version', 'source', 'journal', 'title', 'abstract', 'authors', 'pub_date', 'journal_doi', 'published_journal_title', 'nb_figures', 'review_process', 'entities', 'assays', 'controlled_variables', 'measured_variables']


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
MATCH (col:VizCollection {name: "refereed-preprints"})-->(subcol:VizSubCollection)-->(paper:VizPaper)
WHERE DATETIME(paper.peer_review_date) > DATETIME($limit_date)
WITH DISTINCT
   subcol, 
   paper{.*, rank: ""} AS paper_j // json serializable
RETURN
    subcol.name AS id,
    COLLECT(DISTINCT paper_j) as papers
  '''
    map = {'limit_date': []}
    returns = ['id', 'papers']


class BY_HYP(Query):

    code = '''
// Using precomputed Viz nodes
MATCH
  (col:VizCollection {name: "by_hyp"})-->(subcol:VizSubCollection),
  (subcol)-->(paper:VizPaper),
  (subcol)-[:HasEntity]->(ctrl_v:VizEntity)-[:HasPotentialEffectOn]->(meas_v:VizEntity)
WHERE DATETIME(paper.pub_date) > DATETIME($limit_date)
WITH DISTINCT paper, ctrl_v, meas_v
ORDER BY
  id(ctrl_v) ASC, // deterministic
  id(meas_v) ASC, // deterministic
  DATETIME(paper.pub_date) DESC
WITH DISTINCT
  paper{.*, rank: ""} AS paper_j, // JSON serializable
  {ctrl_v: COLLECT(DISTINCT ctrl_v.text), meas_v: COLLECT(DISTINCT meas_v.text)} AS hyp
 WITH DISTINCT
  hyp,
  COLLECT(paper_j) AS papers
// assign an id to each hyp-collection of papers
WITH COLLECT([hyp, papers]) AS all_results
UNWIND range(0, size(all_results)-1) as i
RETURN 
  i as id, 
  all_results[i][0] AS hyp, 
  all_results[i][1] AS papers
    '''
    map = {'limit_date': []}
    returns = ['id', 'hyp', 'papers']


class AUTOMAGIC(Query):

    code = '''
// using precomputed Viz nodes
MATCH
  (col:VizCollection {name: "automagic"})-->(subcol:VizSubCollection {name: "covid19"})-->(paper:VizPaper),
  (paper:VizPaper)-[:HasPaperRank]->(rank:VizPaperRank {context: "automagic"}),
  (paper)-[:HasEntity]->(exp_assays:VizEntity {category: "assay"}),
  (paper)-[:HasEntity]->(biol_entities:VizEntity {category: "entity"})
WHERE DATETIME(paper.pub_date) > DATETIME($limit_date)
WITH DISTINCT
  paper, rank.value AS automagic_rank,
  COLLECT(DISTINCT {text: biol_entities.text}) AS exp_assays,
  COLLECT(DISTINCT {text: exp_assays.text}) AS biol_entities
ORDER BY
  automagic_rank ASC //rank is rank sum score
WITH DISTINCT
  paper{.*, rank: automagic_rank} AS paper_j, // JSON serializable
  automagic_rank 
RETURN "covid19" AS id, COLLECT(paper_j) AS papers
    '''
    map = {'limit_date': []}
    returns = ['id', 'papers']


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
WHERE toLower(a.journal_title) = 'biorxiv'
WITH COUNT(DISTINCT a.doi) AS biorxiv_preprints
MATCH (a:VizPaper {query:"by_reviewing_service"})
WITH COUNT(DISTINCT a.doi) AS refereed_preprints, biorxiv_preprints
MATCH (a:SDArticle {source: "eebapi"})
WITH COUNT(DISTINCT a.doi) AS autoannotated_preprints, refereed_preprints, biorxiv_preprints
RETURN biorxiv_preprints, refereed_preprints, autoannotated_preprints
    '''
    returns = ['biorxiv_preprints', 'refereed_preprints', 'autoannotated_preprints']
