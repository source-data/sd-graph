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
MATCH (refprep:VizCollection {name: "refereed-preprints"})-[:HasSubCol]->(revservice:VizSubCollection)
WHERE (revservice.name = $reviewing_service) OR ($reviewing_service = '')
MATCH (revservice)-[:HasPaper]->(vizpaper:VizPaper)
WITH vizpaper.doi AS doi
MATCH (a:Article {doi: doi})
WITH a
WHERE
  (
    toLower(apoc.convert.toString(a.published_journal_title)) = toLower($published_in)
  ) OR ($published_in = '')
WITH DISTINCT
  id(a) AS id,
  a.publication_date AS pub_date,
  a.title AS title,
  a.abstract AS abstract,
  a.version AS version,
  a.doi AS doi,
  a.journal_title as journal,
  a.published_journal_title as published_journal_title,
  a.journal_doi as journal_doi
RETURN id, pub_date, title, abstract, version, doi, journal, published_journal_title, journal_doi
ORDER BY pub_date DESC
SKIP $page * $pagesize
LIMIT $pagesize
    '''
    map = {
      'reviewing_service': {'req_param': 'reviewing_service', 'default': ''},
      'published_in': {'req_param': 'published_in', 'default': ''},
      'pagesize': {'req_param': 'pagesize', 'default': 20},
      'page': {'req_param': 'page', 'default': 0},
    }

    returns = [
      'id', 'pub_date', 'title', 'abstract', 'version', 'doi', 'journal', 'published_journal_title',
      'journal_doi', 'nb_figures'
    ] #, 'review_process']


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


class BY_DOIS(Query):

    code = '''
// Get the most recent version of each article that has one of the given DOIs
UNWIND $dois as doi
WITH
  doi
CALL {
    WITH doi
    MATCH (article:Article {doi: doi})
    WHERE
      (
        toLower(apoc.convert.toString(article.published_journal_title)) = toLower($published_in)
      ) OR ($published_in = '')
    WITH article
    ORDER BY article.version DESC
    return COLLECT(article)[0] AS a
}

OPTIONAL MATCH (a)-[r:HasReview]->(review:Review)
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response)
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH
  a,
  review,
  response,
  annot
ORDER BY
  a.publication_date DESC,
  review.review_idx ASC,
  annot.review_idx ASC
WITH
  a,
  {reviews: COLLECT(DISTINCT review {.*}), response: COLLECT(DISTINCT response {.*})[0], annot: COLLECT(DISTINCT annot {.*})} AS review_process

OPTIONAL MATCH (a)-->(f:Fig)
WITH
  a,
  review_process,
  COUNT(DISTINCT f) AS nb_figures

OPTIONAL MATCH (a)-->(auth:Contrib)
OPTIONAL MATCH (auth)-[:has_orcid]->(auth_id:Contrib_id)
WITH
  a,
  review_process,
  nb_figures,
  auth,
  auth_id
ORDER BY auth.position_idx
WITH
  a,
  review_process,
  nb_figures,
  COLLECT(DISTINCT auth {.surname, .given_names, .position_idx, .corresp, orcid: auth_id.text}) AS authors

OPTIONAL MATCH (vzp:VizPaper {doi: a.doi})
OPTIONAL MATCH (vzp)-[:HasReviewDate]->(revdate:VizReviewDate)
WITH
  a,
  review_process,
  nb_figures,
  authors,
  vzp,
  COLLECT(revdate)[0].date AS revdate // There are possibly multiple review dates. Let's just grab the first one.

OPTIONAL MATCH (VizCollection {name: "by-auto-topics"})-->(autotopics:VizSubCollection)-[rel_autotopics_paper]->(vzp)-[:HasEntityHighlight]->(highlight:VizEntity {category: 'entity'})
WITH
  a,
  review_process,
  nb_figures,
  authors,
  vzp,
  revdate,
  COLLECT(DISTINCT autotopics.topics) AS main_topics,
  COLLECT(DISTINCT highlight.text) AS highlighted_entities

OPTIONAL MATCH (vzp)-[:HasEntity]->(assay:VizEntity {category: 'assay'})
WITH
  a,
  review_process,
  nb_figures,
  authors,
  vzp,
  revdate,
  main_topics,
  highlighted_entities,
  COLLECT(DISTINCT assay.text) AS assays

OPTIONAL MATCH (vzp)-[:HasEntity]->(entity:VizEntity {category: 'entity'})
// don't duplicate entities if they are in the topic highlight set
WHERE not((vzp)-[:HasEntityHighlight]->(entity))
WITH
  a,
  review_process,
  nb_figures,
  authors,
  revdate,
  main_topics,
  highlighted_entities,
  assays,
  COLLECT(DISTINCT entity.text) AS entities

RETURN
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
  review_process,
  nb_figures,
  authors,
  revdate,
  main_topics,
  highlighted_entities,
  assays,
  entities
'''
    map = {
      'dois': {'req_param': 'dois', 'default': []},
      'published_in': {'req_param': 'published_in', 'default': ''}
    }
    returns = [
      'id',
      'doi',
      'version',
      'source',
      'journal',
      'title',
      'abstract',
      'journal_doi',
      'published_journal_title',
      'pub_date',
      'review_process',
      'nb_figures',
      'authors',
      'revdate',
      'entities',
      'assays',
      'main_topics',
      'highlighted_entities',
      'published_in',
      'dois'
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


class _DOCMAP(Query):
    """Base class to filter and construct DocMaps.

    The creation of the DocMaps is encapsulated in `code_docmap_creation`. This
    part remains constant. What is variable is the filtering of the DocMaps.
    That is to be implemented in subclasses by using the class variables
    `code_docmap_filtering` and `map_docmap_filtering`.
    
    `code_docmap_filtering` has to provide a `doi` variable by which preprints
    are filtered. It can be provided as either a single variable or a list
    using the `UNWIND` Cypher syntax. See DOCMAP_BY_DOI and
    DOCMAP_BY_REVSERVICE_AND_INTERVAL for examples.
    """

    code_docmap_creation = '''
// Find all Docmaps that have as input in one of their steps the preprint we're interested in
MATCH (docmapNode:Docmap)<-[:steps]-(:Step)<-[:inputs]-(:Preprint {doi: doi})
WITH DISTINCT docmapNode

// Paging: keep ordering stable through sorting by internal ID, then skip & limit to go to the requested page.
ORDER BY docmapNode.id
SKIP $offset
LIMIT $page_size

// Generate a dict-/map-like object from each Docmap node of interest. There are lots of
// CALL instructions because we want to iterate through the Docmap tree and turn every
// Docmap node's steps, every step's actions, every action's outputs etc into maps that
// end up in the final output object.
CALL {
    WITH docmapNode
    MATCH (docmapNode)<-[:steps]-(stepNode)
    CALL {
        WITH stepNode
        MATCH
          (stepNode)<-[:assertions]-(assertionNode),
          (stepNode)<-[:inputs]-(inputNode),
          (stepNode)<-[:actions]-(actionNode)
        CALL {
            WITH actionNode
            MATCH (actionNode)<-[:outputs]-(outputNode)
            CALL {
              WITH outputNode
              MATCH (outputNode)<-[:content]-(contentNode)
              RETURN outputNode{
                  .*,
                  content: COLLECT(DISTINCT contentNode{.*})
              } AS output
            }
            WITH
                actionNode,
                { outputs: COLLECT(DISTINCT output) } AS action
            OPTIONAL MATCH (actionNode)<-[:participants]-(participantNode)
            WITH
                CASE WHEN participantNode IS NULL THEN
                    action
                ELSE
                    action{
                        .*,
                        participants: COLLECT(
                            DISTINCT {
                                actor: CASE WHEN participantNode.name = "anonymous" THEN {
                                    type: "person",
                                    name: "anonymous"
                                } ELSE {
                                    type: "person",
                                    firstName: participantNode.firstName,
                                    familyName: participantNode.familyName
                                } END,
                                role: participantNode.role
                            }
                        )
                    }
                END AS action
            RETURN action
        }
        WITH
            stepNode,
            {
                inputs: COLLECT(DISTINCT inputNode{.*}),
                assertions: COLLECT(DISTINCT assertionNode{.*}),
                actions: COLLECT(DISTINCT action)
            } AS step
        WITH
            stepNode,
            CASE WHEN stepNode.next_step IS NULL THEN
                step
            ELSE
                step{.*, `next-step`: stepNode.next_step}
            END AS step
        RETURN [
            stepNode.id,
            step
        ] AS id_and_step
    }
    RETURN {
        id: docmapNode.id,
        type: "docmap",
        created: docmapNode.created,
        provider: docmapNode.provider,
        publisher: {
            url: docmapNode.publisher_url,
            name: docmapNode.publisher_name,
            peer_review_policy: docmapNode.publisher_peer_review_policy
        },
        generatedAt: docmapNode.generatedAt,
        `first-step`: docmapNode.first_step,
        steps: apoc.map.fromPairs(COLLECT(id_and_step))
    } as docmap
}
RETURN docmap
'''
    map_docmap_creation = {
      'offset': {
        'req_param': 'offset',
        'default': 0,
      },
      'page_size': {
        'req_param': 'page_size',
        'default': 100,
      },
    }

    code_docmap_filtering = ''
    map_docmap_filtering = {}

    returns = ['docmap']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = f'''{self.__class__.code_docmap_filtering}
{self.__class__.code_docmap_creation}
'''
        self.map = {}
        self.map.update(self.__class__.map_docmap_creation)
        self.map.update(self.__class__.map_docmap_filtering)

class DOCMAP_BY_DOI(_DOCMAP):
    code_docmap_filtering = '''
WITH $doi AS doi
    '''
    map_docmap_filtering = {'doi': {'req_param': 'doi', 'default': ''}}

class DOCMAPS_FROM_REVSERVICE_IN_INTERVAL(_DOCMAP):
    code_docmap_filtering = '''
MATCH
  (col:VizCollection)-[:HasSubCol]->(subcol:VizSubCollection)-[:HasPaper]->(paper:VizPaper),
  (preprint:Preprint)-[:inputs]->(Step)<-[:actions]-(Action)<-[:outputs]-(review:RefereeReport)
WHERE col.name = "refereed-preprints"
  AND subcol.name = $reviewing_service
  AND paper.doi = preprint.doi
WITH preprint, DATETIME(review.published) AS review_publish_date
WHERE review_publish_date >= DATETIME($start_date)
  AND review_publish_date < DATETIME($end_date)
WITH COLLECT(DISTINCT preprint.doi) AS doiList
UNWIND doiList AS doi
    '''
    map_docmap_filtering = {
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
    }

class DOCMAPS_IN_INTERVAL(_DOCMAP):
    code_docmap_filtering = '''
MATCH (preprint:Preprint)-[:inputs]->(Step)<-[:actions]-(Action)<-[:outputs]-(review:RefereeReport)
WITH preprint, DATETIME(review.published) AS review_publish_date
WHERE review_publish_date >= DATETIME($start_date)
  AND review_publish_date < DATETIME($end_date)
WITH COLLECT(DISTINCT preprint.doi) AS doiList
UNWIND doiList AS doi
    '''
    map_docmap_filtering = {
      'start_date': {
        'req_param': 'start_date',
        'default': '1900-01-01',
      },
      'end_date': {
        'req_param': 'end_date',
        'default': '2900-01-01',
      },
    }

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
MATCH
    (col:VizCollection {name: "refereed-preprints"})-[:HasSubCol]->(subcol:VizSubCollection)-[:HasPaper]->(paper:VizPaper)-[:HasReviewDate]->(revdate:VizReviewDate)
WHERE DATETIME(revdate.date) > DATETIME($limit_date)
WITH DISTINCT
    subcol,
    paper{.*, rank: ""} AS paper_j // json serializable
MATCH
    (subcol)-[:HasDesciption]->(descriptor:VizDescriptor)
RETURN
    subcol.name AS id,
    descriptor{.*} AS reviewing_service_description,
    COLLECT(DISTINCT paper_j) as papers
    '''
    map = {
      'limit_date': {'req_param': 'limit_date', 'default':'1900-01-01'}
    }
    returns = ['id', 'papers', 'reviewing_service_description']


class BY_AUTO_TOPICS(Query):

    code = '''
// Using precomputed Viz nodes
MATCH
  (col:VizCollection {name: "by-auto-topics"})-[:HasSubCol]->(subcol:VizSubCollection),
  (subcol)-[subcol_rel_entity:HasEntity]->(entity_highlighted:VizEntity {category: "entity"})
WITH DISTINCT
  col, subcol, entity_highlighted,
  subcol_rel_entity
ORDER BY
  subcol_rel_entity.highlight_score DESC
WITH col, subcol, COLLECT(DISTINCT entity_highlighted.text) AS entities
MATCH
  (subcol)-[subcol_rel_paper:HasPaper]->(paper:VizPaper)
WITH
  col, subcol, entities,
  DATETIME(paper.pub_date) AS pub_date,
  paper{.*, rank: ""} AS paper_j, // JSON serializable
  subcol_rel_paper
ORDER BY
  pub_date DESC,
  subcol_rel_paper.overlap_size DESC
WHERE
  pub_date > DATETIME($limit_date)
WITH
  id(subcol) AS topic_id,
  subcol.name AS topics_name,
  subcol.topics AS topics,
  COLLECT(DISTINCT paper_j) AS paper_collection_j,
  entities,
  COUNT(DISTINCT entities) AS N_entities
ORDER BY
  N_entities DESC
WITH
  COLLECT({topics: topics, topics_name: topics_name, entity_highlighted_names: entities, papers: paper_collection_j}) AS all,
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
  (paper)-[:HasEntity]->(biol_entities:VizEntity {category: "entity"})
WITH DISTINCT
  subcol, 
  paper,
  DATETIME(paper.pub_date) AS pub_date,
  rel_to_paper.rank AS automagic_rank,
  COLLECT(DISTINCT biol_entities.text) AS biol_entities
ORDER BY
  automagic_rank ASC,
  pub_date DESC
WHERE pub_date > DATETIME($limit_date)
MATCH (paper)-[:HasEntity]->(exp_assays:VizEntity {category: "assay"})
WITH DISTINCT
  subcol, paper, biol_entities, automagic_rank,
  COLLECT(DISTINCT exp_assays.text) AS exp_assays
LIMIT 100
WITH DISTINCT
  subcol,
  paper{.*, rank: automagic_rank, exp_assays: exp_assays, biol_entities: biol_entities} AS paper_j // JSON serializable
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

class STATS(Query):
    code = '''
MATCH (h:UpdateStatus)
RETURN
  h.current_total_nodes AS total_nodes,
  h.current_num_preprints AS preprints,
  h.current_num_refereed_preprints AS refereed_preprints,
  h.current_num_autoannotated_preprints AS autoannotated_preprints,
  h.current_num_docmaps AS num_docmaps,
  h.current_num_reviews AS num_reviews,
  h.update_completed AS last_updated
    '''
    returns = ['total_nodes', 'preprints', 'refereed_preprints', 'autoannotated_preprints', 'num_docmaps', 'num_reviews', 'last_updated']
