// PRECOMPUTE RESULTS

RETURN "purging viz graph" as `preparation step`;
// PURGE PRECOMPUTED
:begin
MATCH (n:VizCollection) DETACH DELETE n;
MATCH (n:VizSubCollection) DETACH DELETE n;
MATCH (n:VizPaper) DETACH DELETE n;
MATCH (n:VizInfo) DETACH DELETE n;
MATCH (n:VizEntity) DETACH DELETE n;
MATCH (n:VizReviewDate) DETACH DELETE n;
MATCH (n:VizPaperRank) DETACH DELETE n;
RETURN "purge" as `completed`;
:commit

// VizPaper for biorxiv preprints
:begin
MATCH (a:SDArticle)
WHERE a.journalName = 'biorxiv'
MERGE (preprint:VizPaper {doi: a.doi, pub_date: toString(DATETIME(a.pub_date))})
RETURN COUNT(preprint) AS `biorxiv preprints vizPapers`;
:commit

// BY REVIEWING SERVICE
:begin
UNWIND [{name: 'review commons', rank: 0}, {name: 'peerage of science', rank: 1}, {name: 'embo press', rank: 2}, {name: 'elife', rank:3}] AS reviewing
MATCH (a:Article)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review {reviewed_by: reviewing.name})
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: reviewing.name})
WITH DISTINCT
    reviewing, a.doi AS doi, review, annot
WHERE 
    EXISTS(review.reviewed_by) OR EXISTS(annot.reviewed_by)
WITH DISTINCT 
  reviewing, doi, 
  COLLECT(DISTINCT DATETIME(review.posting_date)) + COLLECT(DISTINCT DATETIME(annot.posting_date)) AS peer_review_dates
UNWIND peer_review_dates AS peer_review_date
// remove duplicate and sort to hvae most recent peer review date first
WITH DISTINCT
    reviewing, doi, peer_review_date
ORDER BY peer_review_date DESC
// keep most recent peer review date
WITH DISTINCT
    reviewing, doi, COLLECT(DISTINCT peer_review_date)[0] AS earliest_review_date
MATCH
  (paper:VizPaper {doi: doi})
WITH
  reviewing, doi, paper, paper.pub_date AS pub_date, earliest_review_date
ORDER BY
    reviewing.rank ASC, pub_date DESC
MERGE (col:VizCollection {name: "refereed-preprints"})
MERGE (subcol:VizSubCollection {name: reviewing.name})
MERGE (revdate:VizReviewDate {date: earliest_review_date})
MERGE (paper)-[:HasReviewDate]->(revdate)
MERGE (col)-[:HasSubCol]->(subcol)
MERGE (subcol)-[:HasPaper]->(paper)
RETURN COUNT(DISTINCT paper) AS `papers in the by reviewing service`;
:commit

// AUTO TOPICS HIGHLIGHTS
:begin
MATCH
  (topics_collection:SDAutoTopics)-->(highlighted:H_Entity)
WITH
  topics_collection,
  COLLECT(DISTINCT highlighted) AS highlighted_entities
MATCH
  (topics_collection)-->(a:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(entity:H_Entity)
WITH DISTINCT
  topics_collection,
  highlighted_entities,
  a.doi AS doi,
  COLLECT(DISTINCT entity) AS article_entities,
  COUNT(DISTINCT entity) AS N_entities
WITH 
  topics_collection,
  apoc.text.join(topics_collection.topics, ', ') AS topics_name,
  doi,
  highlighted_entities,
  apoc.coll.intersection(highlighted_entities, article_entities) AS overlapping_highlights
WITH
  topics_collection,
  topics_name,
  doi,
  highlighted_entities,
  overlapping_highlights,
  size(overlapping_highlights) AS N_overlap
WHERE N_overlap >= 2
MATCH
  (paper:VizPaper {doi: doi})
WITH
  topics_collection,
  topics_name,
  paper,
  highlighted_entities,
  overlapping_highlights,
  N_overlap
UNWIND highlighted_entities AS highlighted_entity
UNWIND overlapping_highlights as overlapping_highlight
MERGE (col:VizCollection {name: "by-auto-topics"})
MERGE (subcol:VizSubCollection {topics: topics_collection.topics, name: topics_name})
MERGE (col)-[:HasSubCol]->(subcol)
MERGE (subcol)-[:HasPaper {overlap_size: N_overlap}]->(paper)
MERGE (highlight:VizEntity {text: highlighted_entity.name, category: 'topic_highlight'})
MERGE (subcol)-[:HasEntity {highlight_score: highlighted_entity.community_centrality}]->(highlight)
MERGE (overlap:VizEntity {text: overlapping_highlight.name, category: 'paper_highlight'})
MERGE (paper)-[:HasEntity]->(overlap)
RETURN COUNT(DISTINCT paper) AS `papers in the auto topics set`;
:commit

// LINK EXP ASSAYS
:begin
MATCH
  (a:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity)-[:Has_text]->(name:Term)
WHERE
  a.journalName = "biorxiv" AND
  //a.doi = "10.1101/2020.06.29.178129" AND  // for testing
  entity.category = "assay" AND
  t.category = "assay" AND
  size(name.text) > 1  // exclude embarassing artefacts of the not so AI engine
WITH
  // keep only necessary fields and ndoe ids to minimze memory requirements
  a.doi AS doi, id(p) AS panel_id, id(t) AS t_id, name
// link to entity network
MATCH
   (name)<-[:Has_text]-(bridge:H_Entity)
WHERE
  bridge.category = "assay"
// find respective concept id
WITH
  doi, panel_id, name,
  COUNT(DISTINCT t_id) AS freq_in_this_paper,
  bridge.assay_concept_name AS concept_name
ORDER BY freq_in_this_paper DESC
WITH DISTINCT
  // find most frequently used term in paper for each concept
  doi, 
  COLLECT(DISTINCT name.text)[0] AS name_in_this_paper, 
  COUNT(DISTINCT panel_id) AS N_panels,
  // aggregate concepts with same name but different ids due to imperfect community detection
  concept_name 
//cutoff to eliminate terms or concept that are only detected once
WHERE N_panels >= 2
// build viz graph
MATCH
  (paper:VizPaper {doi: doi})
WITH
  paper, name_in_this_paper
MERGE (entity:VizEntity {text: name_in_this_paper, category: 'assay'})
MERGE (paper)-[:HasEntity]->(entity)
RETURN COUNT(DISTINCT entity) AS `linked assays for visualization`; 
:commit

// LINK GENEPROD
:begin
MATCH 
  (a:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity)-[:Has_text]->(name:Term)
WHERE
  a.journalName = "biorxiv" AND
  // a.doi = "10.1101/2020.06.29.178129" AND  // for testing
  entity.type IN ["gene", "protein", "geneprod"] AND
  t.type IN ["gene", "protein", "geneprod"]
WITH
  // keep only necessary fields and ndoe ids to minimze memory requirements
  a.doi AS doi, id(p) AS panel_id, id(t) AS t_id, name, entity
WHERE
  (size(name.text) > 1 OR name.text = "s" )  // exclude embarassing artefacts of the not so AI engine but keep spike S SARS protein
// link to entity network
MATCH
  (name)<-[:Has_text]-(bridge:H_Entity)
WHERE
  // geneprod or  protein or genes
  bridge.type IN ["gene", "protein", "geneprod"]
// find respective concept id
WITH
  doi, panel_id, name,
  COUNT(DISTINCT t_id) AS freq_in_this_paper,
  bridge.geneprod_concept_name AS concept_name
ORDER BY freq_in_this_paper DESC
WITH
  doi,
  // find most frequently used term in paper for each concept name
  COLLECT(DISTINCT name.text)[0] AS name_in_this_paper,
  COUNT(DISTINCT panel_id) AS N_panels,
  concept_name
//cutoff to eliminate terms or concept that are only detected once
WHERE N_panels >= 2
// build viz graph
MATCH
  (paper:VizPaper {doi: doi})
WITH
  paper, name_in_this_paper
MERGE (entity:VizEntity {text: name_in_this_paper, category: 'entity'})
MERGE (paper)-[:HasEntity]->(entity)
RETURN COUNT(DISTINCT entity) AS `linked geneprod for visualization`;
:commit


// NON GENEPROD ENTITIES
// MATCH (col:SDCollection)-[:has_article]->(a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure),
// (f)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "entity"})-[:Has_text]->(name:Term)
// WHERE
//   NOT (entity.type = "gene" OR entity.type = "protein" OR entity.type = "geneprod") AND 
//   (size(name.text) > 1 OR toLower(name.text) = "s" ) // exclude embarassing artefacts of the not so AI engine but keep spike S SARS protein
// WITH DISTINCT
//   a, p, entity, name
// //find synonyms
// MATCH
//    (name)<-[:Has_text]-(s:H_Entity {category: "entity", type: entity.type})
// WITH
//   a, p, entity, name, s
// OPTIONAL MATCH (s)-[:Has_text]->(syn1:Term)
// //combine synonyms
// WITH DISTINCT
//   a, entity, COUNT(DISTINCT p) AS N_panels, 
//   COLLECT(DISTINCT name) + COLLECT(DISTINCT syn1) AS all_synonyms
// UNWIND all_synonyms AS syn
// // remove duplicates
// WITH DISTINCT
//   a, entity, N_panels, syn
// // use most popular synonym
// ORDER BY syn.freq_in_panel DESC
// WITH DISTINCT
//   a, entity, N_panels, COLLECT(DISTINCT syn)[0] AS most_used
// ORDER BY id(entity)
// //collapse identical synonym groups
// WITH DISTINCT
//   a, COLLECT(DISTINCT entity.name)[0] AS representative_entity, SUM(N_panels) AS N, most_used
// WHERE N > 3
// WITH DISTINCT
//   a, 
//   COLLECT(DISTINCT representative_entity) AS entity_names, 
//   COUNT(DISTINCT representative_entity) AS N_entities
// //create info and entities for visualization

// MERGE (paper:VizPaper {doi: a.doi, pub_date: toString(DATETIME(a.pub_date))})
// WITH paper, entity_names
// UNWIND entity_names AS text
// MERGE (entity:VizEntity {text: text, category: "entity"})
// MERGE (paper)-[:HasEntity]->(entity)
// RETURN COUNT(DISTINCT entity) AS `linked entities for visualization`;


// AUTOMAGIC
// sum of ranks for recent papers
// rank by assay
:begin
MATCH (coll:SDCollection)-->(a:SDArticle {journalName:'biorxiv'})
// recent papers
WHERE
  DATETIME(a.pub_date) > (DATETIME() - duration({months: 3}))
WITH
  a.doi AS doi
// IMPORTANT: when in a tie, preprints will still be ordered by pub date
ORDER BY DATETIME(a.pub_date) DESC
MATCH 
  (viza:VizPaper {doi: doi})-[:HasEntity]->(assay:VizEntity {category: 'assay'})
WITH DISTINCT
   viza,
   COUNT(DISTINCT assay) AS N_assays,
   COLLECT(DISTINCT assay.text) AS assays
// aggregate now by N_assays to collect preprint with same number of assays
// WITH DISTINCT
//   preprints_with_assays,
//   COLLECT(DISTINCT viza) AS preprints_by_N_assays,
//   N_assays
ORDER BY N_assays DESC
WITH
  // COLLECT(DISTINCT preprints_by_N_assays) as preprint_list_of_lists
  COLLECT(DISTINCT [viza, assays]) AS preprint_list,
  COUNT(DISTINCT viza) AS N
WITH 
  preprint_list,
  N
  //preprint_list_of_lists,
  //size(preprint_list_of_lists) AS N
UNWIND range(0, N-1) as i
// multilpe preprints with same N_assays can have the same rank (tie)
//UNWIND preprint_list_of_lists[i] AS preprint
WITH
  COLLECT({rank: i, preprint: preprint_list[i]}) AS ranked_by_assays
// rank by entities
MATCH (coll:SDCollection)-->(a:SDArticle {journalName:'biorxiv'})
WHERE
  DATETIME(a.pub_date) > (DATETIME() - duration({months: 3}))
WITH
  ranked_by_assays,
  a.doi AS doi
// IMPORTANT: when ties, preprint will still be ordered by pub date...  
ORDER BY DATETIME(a.pub_date) DESC
MATCH (viza:VizPaper {doi: doi})-[:HasEntity]->(entity:VizEntity {category: 'entity'})
WITH
  ranked_by_assays,
  viza, 
  COUNT(DISTINCT entity) AS N_entities,
  COLLECT(DISTINCT entity.text) AS entities
// WITH DISTINCT
//   ranked_by_assays,
//   N_intersection, 
//   COLLECT(DISTINCT viza) AS preprint_by_N_entities,
//   N_entities
ORDER BY N_entities DESC
WITH
  ranked_by_assays,
  // COLLECT(DISTINCT preprint_by_N_entities) AS preprint_list_of_lists
  COLLECT(DISTINCT [viza, entities]) AS preprint_list,
  COUNT(DISTINCT viza) AS N
WITH 
  ranked_by_assays,
  preprint_list,
  N
  // preprint_list_of_lists,
  // size(preprint_list_of_lists) AS N
UNWIND range(0, N-1) AS i
// UNWIND preprint_list_of_lists[i] AS preprint
WITH
  ranked_by_assays,
  COLLECT({rank: i, preprint: preprint_list[i]}) AS ranked_by_entities

// rank by multi topics
MATCH (coll:SDCollection)-->(a:SDArticle {journalName:'biorxiv'})
// recent papers
WHERE
  DATETIME(a.pub_date) > (DATETIME() - duration({months: 3}))
WITH
  ranked_by_assays, ranked_by_entities,
  a.doi AS doi
MATCH
  (col:VizCollection {name: "by-auto-topics"})-->(topic:VizSubCollection)-[rel_autotopics_paper]->(viza:VizPaper {doi: doi})
WHERE
  rel_autotopics_paper.overlap_size >= 2
WITH DISTINCT
  ranked_by_assays, ranked_by_entities,
  viza,
  COUNT(DISTINCT topic) AS N_topics,
  COLLECT(DISTINCT topic.name) AS topics
// IMPORTANT: when ties, preprint will still be ordered by pub date...  
ORDER BY
  N_topics DESC
WITH DISTINCT
  ranked_by_assays, ranked_by_entities,
  COLLECT(DISTINCT [viza, topics]) AS preprint_list,
  COUNT(DISTINCT viza) AS N
UNWIND range(0, N-1) AS i
WITH
  ranked_by_assays, ranked_by_entities,
  COLLECT({rank:i, preprint: preprint_list[i]}) AS ranked_by_topics


// rank by presence of peer reviews
MATCH
  (col:VizCollection {name: "refereed-preprints"})-->(sub:VizSubCollection)-->(a:VizPaper)

// recent papers
WHERE
  DATETIME(a.pub_date) > (DATETIME() - duration({months: 3}))
WITH DISTINCT
  ranked_by_assays, ranked_by_entities, ranked_by_topics,
  a.doi as doi
    
MATCH
  (viza:VizPaper {doi: doi})
OPTIONAL MATCH
  (:Article {doi: doi})-[:HasReview]->(review:Review)
OPTIONAL MATCH
  (:Article {doi: doi})-[:HasAnnot]->(annot:PeerReviewMaterial)
WITH DISTINCT
  ranked_by_assays, ranked_by_entities, ranked_by_topics,
  viza,
  CASE 
    WHEN EXISTS(review.reviewed_by) THEN review.reviewed_by
    ELSE annot.reviewed_by
  END AS reviewed_by
WITH DISTINCT
  ranked_by_assays, ranked_by_entities, ranked_by_topics,
  viza,
  COLLECT(DISTINCT reviewed_by) AS reviewers
WITH DISTINCT
  ranked_by_assays, ranked_by_entities, ranked_by_topics,
  COLLECT(DISTINCT {rank: 0, preprint: [viza,  reviewers]}) AS ranked_by_peerreview
//Sum of ranks for preprints present in both lists
WITH
  ranked_by_assays + ranked_by_entities + ranked_by_topics + ranked_by_peerreview AS ranked_items,
  apoc.coll.max([size(ranked_by_assays), size(ranked_by_entities), size(ranked_by_topics)]) AS max_rank 
UNWIND ranked_items as item
// aggregate by preprint and sum the ranks
WITH DISTINCT 
  item.preprint[0] as preprint,
  COLLECT(item.preprint[1]) AS stuff,
  COLLECT(item.rank) AS ranks,
  COUNT(item.rank) AS N_ranks,
  max_rank
WITH
  preprint, N_ranks, ranks, stuff,
  CASE
    // preprint that appear in a single list will have only one rank that will be added to the max rank
    WHEN N_ranks = 4 THEN apoc.coll.sum(ranks)
    WHEN N_ranks = 3 THEN apoc.coll.sum(ranks) + max_rank
    WHEN N_ranks = 2 THEN apoc.coll.sum(ranks) + 2 * max_rank
    ELSE ranks[0] + 3 * max_rank
  END AS rank_sum
WITH preprint, rank_sum
ORDER BY rank_sum ASC
MERGE (automagic:VizCollection {name: 'automagic'})
MERGE (recent:VizSubCollection {name: 'recent'})
MERGE (automagic)-[:HasSubCol]->(recent)
MERGE (recent)-[:HasPaper {rank: rank_sum, context: 'automagic'}]->(preprint)
RETURN COUNT(DISTINCT preprint) AS `papers in the automagic set`;
:commit