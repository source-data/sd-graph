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
  {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: COLLECT(DISTINCT annot {.*})} AS review_process
WHERE
  review_process.reviews <> [] OR EXISTS(review_process.annot)
RETURN id, pub_date, title, abstract, version, doi, journal, review_process
ORDER BY pub_date DESC
    '''
    returns = ['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'nb_figures', 'review_process']


class COLLECTION_NAMES(Query):
    code = '''
MATCH (subject:Subject)
RETURN subject.text AS subject
    '''
    returns = ['subject']


class SUBJECT_COLLECTIONS(Query):

    code = '''
MATCH (a:Article)-[:has_subject]->(subject:Subject)
WHERE toLower(subject.text) = toLower($subject)
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
    map = {'subject': {'req_param': 'subject', 'default': ''}}
    returns = ['id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'score']


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
OPTIONAL MATCH (vzp:VizPaper {doi: $doi})
OPTIONAL MATCH (vzp)-[:HasReviewDate]->(revdate:VizReviewDate)
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
  DATETIME(a.publication_date) AS pub_date, // pub date as preprint! 
  COUNT(DISTINCT f) AS nb_figures,
  auth,
  vzp, revdate.date AS revdate,
  review, response, annot
OPTIONAL MATCH (auth)-[:has_orcid]->(auth_id:Contrib_id)
OPTIONAL MATCH
  (col:VizCollection {name: "by-auto-topics"})-->(autotopics:VizSubCollection)-[rel_autotopics_paper]->(vzp)-[:HasEntityHighlight]->(highlight:VizEntity {category: 'entity'})
WITH
  id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title,
  nb_figures, auth,
  auth_id.text AS ORCID,
  vzp, revdate,
  review, response, annot,
  COLLECT(DISTINCT autotopics.topics) AS main_topics,
  COLLECT(DISTINCT highlight.text) AS highlighted_entities
OPTIONAL MATCH
  (vzp)-[:HasEntity]->(assay:VizEntity {category: 'assay'})
OPTIONAL MATCH
  (vzp)-[:HasEntity]->(entity:VizEntity {category: 'entity'})
WHERE
  // don't duplicated entities if they are in the topic highlight set
  NOT entity.text IN highlighted_entities
WITH
  id, doi, version, source, journal, title, abstract, pub_date, journal_doi, published_journal_title,
  nb_figures, auth,
  ORCID,
  vzp, revdate,
  review, response, annot,
  main_topics, highlighted_entities,
  COLLECT(DISTINCT assay.text) AS assays,
  COLLECT(DISTINCT entity.text) AS entities
ORDER BY
  pub_date DESC,
  review.review_idx ASC,
  annot.review_idx ASC,
  auth.position_idx ASC
WITH
  id, doi, version, source, journal, title, abstract, toString(pub_date) AS pub_date, journal_doi, published_journal_title, nb_figures, auth, ORCID,
  {reviews: COLLECT(DISTINCT review {.*}), response: response {.*}, annot: COLLECT(DISTINCT annot {.*})} AS review_process,
  revdate,
  entities, assays,
  main_topics, highlighted_entities
RETURN DISTINCT 
  id, doi, version, source, journal, title, abstract, pub_date, nb_figures,
  journal_doi, published_journal_title, COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: ORCID}) AS authors,
  review_process,
  revdate,
  entities, assays,
  main_topics, highlighted_entities
    '''
    map = {'doi': {'req_param': 'doi', 'default': ''}}
    returns = [
      'id', 'doi', 'version', 'source', 'journal', 'title', 'abstract',
      'authors', 'pub_date', 'journal_doi', 'published_journal_title', 'nb_figures',
      'revdate', 'review_process', 'entities', 'assays',
      'main_topics', 'highlighted_entities'
    ]


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
    map = {
      'doi': {'req_param': 'doi', 'default':''},
      'position_idx': {'req_param': 'position_idx', 'default': ''}
    }
    returns = ['doi', 'version', 'title', 'fig_title', 'fig_label', 'caption', 'fig_idx']


class PANEL_BY_NEO_ID(Query):

    code = '''
MATCH (p:Panel)-->(ctCondTag)-->(h:H_Entity)
WHERE id(p) = $id
RETURN p.caption AS caption, COLLECT(DISTINCT h) AS tags
    '''
    returns = ['caption', 'tags']
    map = {'id': {'req_param': 'id', 'default': ''}}


class REVIEW_PROCESS_BY_DOI(Query):

    code = '''
MATCH (a:Article {doi: $doi})-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH a, review, response, annot
ORDER BY review.review_idx ASC
RETURN a.doi as doi, {reviews: COLLECT(DISTINCT review {.*, id: id(review)}), response: response {.*, id: id(response)}, annot: annot {.*, id: id(annot)}} AS review_process
  '''
    map = {'doi': {'req_param': 'doi', 'default': ''}}
    returns = ['doi', 'review_process']


class DOCMAP_BY_DOI(Query):
    code = '''
MATCH
  (docmap:Docmap)<-[:steps]-(step_1:Step),
  (step_1)<-[:inputs]-(preprint:Preprint {doi: $doi}),
  (step_1)<-[:actions]-(reviewing_action:Action),
  (reviewing_action)<-[:outputs]-(review:RefereeReport),
  (review)<-[:content]-(review_content:Content),
  (step_1)<-[:assertions]-(assertion_1:Assertion)
OPTIONAL MATCH
  (reviewing_action)<-[:participants]-(reviewer:Person),
  (docmap)<-[:steps]-(step_2:Step),
  (step_2)<-[:inputs]-(review),
  (step_2)<-[:actions]-(replying_action:Action),
  (replying_action)<-[:participants]-(author:Person),
  (replying_action)<-[:outputs]-(reply:AuthorReply),
  (reply)<-[:content]-(reply_content:Content),
  (step_2)<-[:assertions]-(assertion_2:Assertion)
WITH DISTINCT
  docmap, preprint,
  step_1, assertion_1, reviewing_action, review, review_content, reviewer,
  step_2, assertion_2, reply, reply_content, author
//ORDER BY reviewing_action.index
WITH DISTINCT
  docmap, preprint,
  step_1, assertion_1, review, reviewer,
  COLLECT(DISTINCT review_content) AS review_content_list,
  step_2, assertion_2, reply, author,
  COLLECT(DISTINCT reply_content) AS reply_content_list
WITH DISTINCT
  docmap, preprint,
  step_1, assertion_1, review, reviewer, review_content_list,
  CASE
    WHEN reviewer IS NOT NULL THEN
      [
        {
          actor: {
            type: "person",
            name: reviewer.name
          },
          role: reviewer.role
        }
      ]
    ELSE NULL
  END AS participants,
  step_2, assertion_2, reply, author, reply_content_list
WITH DISTINCT
  docmap, preprint,
  step_1, assertion_1, review, participants,
  {
    // participants: participants,  // deferring assignment of participants to check for null
    outputs: [review{
        type: "review",
        .*,
        content: review_content_list
      }
    ]
  } AS reviewing_action,
  step_2, assertion_2,
  reply{
      type: "author-response",
      .*,
      content: reply_content_list
  } AS reply_action_output,
  COLLECT(DISTINCT
    {
      actor: {
        type: "person",
        firstName: author.firstName,
        familyName: author.familyName
      },
      role: author.role
    }
  ) AS participating_authors
WITH
  docmap, preprint,
  step_1, assertion_1, review,
  step_2, assertion_2,
  CASE
    WHEN participants IS NOT NULL THEN
       reviewing_action{.*, participants: participants}
    ELSE
      reviewing_action
  END AS reviewing_action,
  reply_action_output, participating_authors
WITH DISTINCT
    docmap,
    step_1,
    {
      assertions: [assertion_1{.*}],
      // `next-step`: step_1.next_step, // note: deferring next-step assignment to be able to check for null
      inputs: [preprint{.*}],
      actions: COLLECT(reviewing_action)
    } AS step_1_json,
    step_2,
    {
      assertions: [assertion_2{.*}],
      inputs: COLLECT(DISTINCT review{.uri}),
      actions: [
        {
          participants: participating_authors,
          outputs: reply_action_output
        }
      ]
    } AS step_2_json
WITH DISTINCT
  docmap,
  step_1,
  step_2, step_2_json,
  CASE
    WHEN step_2 IS NOT NULL THEN
      step_1_json{.*, `next-step`: step_1.next_step}
    ELSE
      step_1_json
  END AS step_1_json
WITH DISTINCT
  docmap.id AS id,
  "docmap" AS type,
  docmap.created AS created,
  docmap.publisher AS publisher,
  docmap.provider AS provider,
  docmap.generatedAt AS generatedAt,
  docmap.first_step AS `first-step`,
  CASE WHEN step_2 IS NOT NULL THEN
    apoc.map.fromPairs([
      [step_1.id, step_1_json],
      [step_2.id, step_2_json]
    ])
  ELSE
    apoc.map.fromPairs([
      [step_1.id, step_1_json]
    ])
  END AS steps
RETURN {
  id: id,
  type: type,
  created: created,
  publisher: publisher,
  provider: provider,
  generatedAt: generatedAt,
  `first-step`: `first-step`,
  steps: steps
} AS docmap
'''
    returns = ['docmap']
    # returns = ['id', 'type', 'created', 'publisher', 'provider', 'generatedAt', 'first-step', 'steps']
    map = {'doi': {'req_param': 'doi', 'default': ''}}


class REVIEW_MATERIAL_BY_ID(Query):
    code = '''
MATCH (r)
WHERE
   id(r) = $id AND labels(r)[0] IN ['Review', 'Response', 'PeerReviewMaterial']
WITH
   r, id(r) AS id, labels(r)[0] As content_type,
   r.related_article_doi as doi,
   r.posting_date as posting_date,
   r.text AS content
MATCH
   (rs:ReviewingService {name: r.reviewed_by})
WITH
  r, id, doi, posting_date, content_type, content,
  CASE content_type
    WHEN 'Review' THEN
      {
        contentType: "review",
        id: id,
        content: content,
        provider: $root,
        relatedArticle: [
            {
                content: "https://www.biorxiv.org/content/" + doi,
                doi: doi
            }
        ],
        asserter: rs.url,
        assertedOn: posting_date,
        createdOn: posting_date,
        completedOn: posting_date,
        runningNumber: r.review_idx,
        contributors: [
            "anonymous"
        ]
      }
    WHEN 'Response' THEN
      {
        contentType: "response",
        id: id,
        relatedArticle: [
            {
                content: "https://www.biorxiv.org/content/" + doi,
                doi: doi
            }
        ],
        content: content,
        provider: $root,
        asserter: rs.url,
        assertedOn: r.posting_date
      }
    WHEN 'PeerReviewMaterial' THEN
      {
          contentType: "peer-review-material",
          id: id,
          relatedArticle: [
              {
                  content: "https://www.biorxiv.org/content/" + doi,
                  doi: doi
              }
          ],
          content: content,
          provider: $root,
          asserter: rs.url,
          assertedOn: posting_date
        }
    ELSE {}
  END AS docmap
RETURN docmap
    '''
    map = {
      'id': {'req_param': 'node_id', 'default': ''},
      'root': {'req_param': 'root', 'default': 'https://eeb.embo.org'}
    }
    returns = ['docmap']


class DESCRIBE_REVIEWING_SERVICES(Query):
    code = '''
MATCH (r:ReviewingService)
RETURN
    r.name AS name,
    r.url AS url,
    r.peer_review_policy AS peer_review_policy,
    r.author_driven_submissions AS author_driven_submissions,
    r.post_review_decision AS post_review_decision,
    r.pre_review_triage AS pre_review_triage
    '''
    returns = ['name', 'url', 'peer_review_policy', 'author_driven_submissions', 'post_review_decision', 'pre_review_triage']


class BY_REVIEWING_SERVICE(Query):

    code = '''
// Using precomputed Viz nodes
MATCH (col:VizCollection {name: "refereed-preprints"})-[:HasSubCol]->(subcol:VizSubCollection)-[:HasPaper]->(paper:VizPaper)-[:HasReviewDate]->(revdate:VizReviewDate)
WHERE DATETIME(revdate.date) > DATETIME($limit_date)
WITH DISTINCT
   subcol,
   paper{.*, rank: ""} AS paper_j // json serializable
MATCH (rev:ReviewingService {name: subcol.name})
RETURN
    subcol.name AS id,
    rev{.*} AS reviewing_service_description,
    COLLECT(DISTINCT paper_j) as papers
  '''
    map = {'limit_date': {'req_param': 'limit_date', 'default':'1900-01-01'}}
    returns = ['id', 'papers', 'reviewing_service_description']


class BY_AUTO_TOPICS(Query):

    code = '''
// Using precomputed Viz nodes
MATCH
  (col:VizCollection {name: "by-auto-topics"})-[:HasSubCol]->(subcol:VizSubCollection),
  (subcol)-[subcol_rel_paper:HasPaper]->(paper:VizPaper),
  (subcol)-[subcol_rel_entity:HasEntity]->(entity_highlighted:VizEntity {category: "entity"})
WHERE
  (DATETIME(paper.pub_date) > DATETIME($limit_date))
WITH
  id(subcol) AS topic_id,
  subcol.name AS topics_name,
  subcol_rel_paper,
  paper.pub_date AS pub_date,
  paper{.*, rank: ""} AS paper_j, // JSON serializable
  subcol_rel_entity,
  entity_highlighted.text as entity_highlighted_name,
  subcol.topics AS topics
  //paper_highlight
ORDER BY
  subcol_rel_paper.overlap_size DESC,
  subcol_rel_entity.highlight_score DESC,
  DATETIME(pub_date) DESC
WITH
  topic_id,
  topics_name,
  topics,
  COLLECT(DISTINCT entity_highlighted_name) AS entity_highlighted_names,
  COLLECT(DISTINCT paper_j) AS paper_collection_j,
  COUNT(DISTINCT entity_highlighted_name) AS N_entities
// assign an id to each subcollection of papers
ORDER BY
   N_entities DESC
WITH
  COLLECT({topics: topics, topics_name: topics_name, entity_highlighted_names: entity_highlighted_names, papers: paper_collection_j}) AS all,
  COUNT(DISTINCT topic_id) AS N
UNWIND range(0, N-1) AS id
RETURN 
  id,
  all[id].topics AS topics,
  all[id].topics_name AS topics_name,
  all[id].entity_highlighted_names AS entity_highlighted_names,
  all[id].papers AS papers
    '''
    map = {'limit_date': {'req_param': 'limit_date', 'default':'1900-01-01'}}
    returns = ['id', 'topics', 'topics_name', 'entity_highlighted_names', 'papers']


class AUTOMAGIC(Query):

    code = '''
// using precomputed Viz nodes
MATCH
  (col:VizCollection {name: "automagic"})-->(subcol:VizSubCollection {name: "recent"})-[rel_to_paper:HasPaper {context: 'automagic'}]->(paper:VizPaper),
  (paper)-[:HasEntity]->(exp_assays:VizEntity {category: "assay"}),
  (paper)-[:HasEntity]->(biol_entities:VizEntity {category: "entity"})
WHERE DATETIME(paper.pub_date) > DATETIME($limit_date)
WITH DISTINCT
  subcol, 
  paper,
  rel_to_paper.rank AS automagic_rank,
  COLLECT(DISTINCT biol_entities.text) AS biol_entities,
  COLLECT(DISTINCT exp_assays.text) AS exp_assays
ORDER BY
  automagic_rank ASC,
  DATETIME(paper.pub_date) DESC
LIMIT 100
WITH DISTINCT
  subcol,
  paper{.*, rank: automagic_rank, exp_assays:exp_assays, biol_entities: biol_entities} AS paper_j // JSON serializable
RETURN subcol.name AS id, COLLECT(paper_j) AS papers
    '''
    map = {'limit_date': {'req_param': 'limit_date', 'default':'1900-01-01'}}
    returns = ['id', 'papers']


class LUCENE_SEARCH(Query):
    code = '''
// Full-text search on multiple indices.

CALL {

  ////////// SEARCH TITLE /////////
  //INDEXING: CALL db.index.fulltext.createNodeIndex("title", ["SDArticle"], ["title"]);
  WITH $query AS query
  CALL db.index.fulltext.queryNodes("title", query) YIELD node, score
  WITH node, score, query
  WHERE node.journalName IN ["biorxiv", "medrxiv"]
  WITH
    // weight 1x for results on title
    node.doi AS doi, node.title AS text, 1 * score AS weighted_score, "title" AS source, query
  ORDER BY weighted_score DESC
  RETURN 
  // entities is obligatory field for info for compatibility with the other methods
    doi, [{title: "'" + query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query

  UNION

  ////////// SEARCH ABSTRACT /////////
  //CALL db.index.fulltext.createNodeIndex("abstract",["SDArticle"], ["abstract"]);
  WITH $query AS query
  CALL db.index.fulltext.queryNodes("abstract", query) YIELD node, score
  WITH node, score, query
  WHERE node.journalName IN ["biorxiv", "medrxiv"]
  WITH
    node.doi AS doi, node.title as text, 1 * score AS weighted_score, "abstract" AS source, query
  ORDER BY weighted_score DESC
  RETURN 
    doi, [{title: "'" + query + "' found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
  LIMIT 20

  UNION

  ///////// SEARCH AUTHORS /////////
  //INDEXED WITH: CALL db.index.fulltext.createNodeIndex("name",["SDContrib"], ["concat_name", "surname"]);
  WITH $query AS query
  CALL db.index.fulltext.queryNodes("name", query) YIELD node, score
  WITH id(node) AS id, score, query
  MATCH (author:SDContrib)
  WHERE id(author) = id
  WITH DISTINCT author, score, query
  MATCH (article:SDArticle)-[:has_author]->(author)
  WHERE article.journalName IN ["biorxiv", "medrxiv"]
  WITH
  //weight 4x for results on authors
    article.doi as doi, author.surname as text, 2 * score AS weighted_score, "author list" AS source, query
  ORDER BY weighted_score DESC
  RETURN 
    doi, [{title: query + " found in " + source, text: text, entities: []}] AS info, weighted_score, source, query
  LIMIT 20
}
RETURN doi, info, weighted_score, source, query
ORDER BY weighted_score DESC
LIMIT 10
'''
    map = {'query': {'req_param': 'search_string', 'default': ''}}
    returns = ['doi', 'info', 'score', 'source', 'query']


class SEARCH_DOI(Query):
    code = '''
WITH $query AS query
MATCH (article:SDArticle)
WHERE article.doi = query
RETURN
  article.doi AS doi, [{title: 'doi match', text: article.doi, entities:[]}] AS info, 10.0 AS score, 'doi' AS source, query
'''
    map = {'query': {'req_param': 'search_string', 'default': ''}}
    returns = ['doi', 'info', 'score', 'source', 'query']

class SEARCH_REVIEWS(Query):
    code = '''
MATCH (
  col:VizCollection {name: "refereed-preprints"}
)-[:HasSubCol]->(
  subcol:VizSubCollection
)-[:HasPaper]->(
  paper:VizPaper
)-[:HasReviewDate]->(
  revdate:VizReviewDate
)
WHERE DATETIME(revdate.date) >= DATETIME($start_date)
   AND DATETIME(revdate.date) < DATETIME($end_date)
   AND subcol.name = $reviewing_service
RETURN paper.doi AS doi
ORDER BY revdate.date
SKIP $offset
LIMIT $page_size
'''
    map = {
      'reviewing_service': {
        'req_param': 'reviewing_service',
        'default': '',
      },
      'start_date': {
        'req_param': 'start_date',
        'default': '1900-01-01',
      },
      'end_date': {
        'req_param': 'end_date',
        'default': '2900-01-01',
      },
      'offset': {
        'req_param': 'offset',
        'default': 0,
      },
      'page_size': {
        'req_param': 'page_size',
        'default': 100,
      },
    }
    returns = ['doi']

class STATS(Query):
    code = '''
MATCH (h:UpdateStatus)
RETURN
  h.current_total_nodes AS total_nodes,
  h.current_num_preprints AS preprints,
  h.current_num_refereed_preprints AS refereed_preprints,
  h.current_num_autoannotated_preprints AS autoannotated_preprints,
  h.update_completed AS last_updated
    '''
    returns = ['total_nodes', 'preprints', 'refereed_preprints', 'autoannotated_preprints', 'last_updated']
