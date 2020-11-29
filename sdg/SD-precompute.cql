// PRECOMPUTE RESULTS

RETURN "purging viz graph" as `preparation step`;
// PURGE PRECOMPUTED

MATCH (n:VizCollection) DETACH DELETE n;
MATCH (n:VizSubCollection) DETACH DELETE n;
MATCH (n:VizPaper) DETACH DELETE n;
MATCH (n:VizInfo) DETACH DELETE n;
MATCH (n:VizEntity) DETACH DELETE n;
MATCH (n:VizReviewDate) DETACH DELETE n;
MATCH (n:VizPaperRank) DETACH DELETE n;
RETURN "purge" as `completed`;

// BY REVIEWING SERVICE

UNWIND [{name: 'review commons', rank: 0}, {name: 'peerage of science', rank: 1}, {name: 'embo press', rank: 2}, {name: 'elife', rank:3}] AS reviewing
MATCH (a:Article)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review {reviewed_by: reviewing.name})
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: reviewing.name})
WITH DISTINCT
    reviewing, a, review, annot
WHERE 
    EXISTS(review.text) OR EXISTS(annot.text)
WITH DISTINCT reviewing, a, review, annot, a.version AS version
ORDER BY version DESC
// keep only the most recent version of the article
WITH DISTINCT reviewing, COLLECT(DISTINCT a)[0] AS most_recent, review, annot
// get the figures
MATCH (most_recent)-->(f:Fig) // even prelim entries from source: "biorxiv_crossref" have empty figures instead of NULL
// eliminate figures without a caption such as graphical abstracts etc
WHERE EXISTS(f.caption) AND EXISTS(f.label)
//identify the most recent peer review date from review or from peer review material
WITH DISTINCT
    reviewing, most_recent, f,
    COLLECT(DISTINCT toString(DATETIME(review.posting_date))) + COLLECT(DISTINCT toString(DATETIME(annot.posting_date))) AS peer_review_dates
UNWIND peer_review_dates AS peer_review_date
// remove duplicate and sort to hvae most recent peer review date first
WITH DISTINCT
    reviewing, most_recent, f, peer_review_date
ORDER BY peer_review_date DESC
// keep most recent peer review date
WITH DISTINCT
    reviewing, most_recent, f, COLLECT(DISTINCT peer_review_date)[0] AS review_date
// retrieve now the actual peer reviews
OPTIONAL MATCH (most_recent)-[:HasReview]->(review:Review {reviewed_by: reviewing.name})
OPTIONAL MATCH (most_recent)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: reviewing.name})
WITH DISTINCT
    reviewing, review_date, most_recent.doi AS doi, most_recent.publication_date AS pub_date, 
    f.label AS fig_label, f.caption AS caption, f.position_idx AS position_idx
ORDER BY
    reviewing.rank ASC, pub_date DESC, position_idx ASC
// TODO: replace id: reviewing.name and query by a VizCollection and VizSubCollection?
MERGE (col:VizCollection {name: "refereed-preprints"})
MERGE (subcol:VizSubCollection {name: reviewing.name})
// VizPaper needs all field required for sorting, filtering and ranking
MERGE (paper:VizPaper {doi: doi, pub_date: pub_date})
MERGE (revdate:VizReviewDate {date: review_date})
MERGE (paper)-[:HasReviewDate]->(revdate)
MERGE (col)-[:HasSubCol]->(subcol)
MERGE (subcol)-[:HasPaper]->(paper)
MERGE (info:VizInfo {doi: doi, title: fig_label, text: caption, rank: position_idx, id: position_idx, info_type: "fig-caption"}) // MERGE cannot be used if properties are NULL; this is why prelim entries are linked to empty figs
MERGE (paper)-[:HasInfo]->(info)
//RETURN paper, info;
RETURN COUNT(DISTINCT paper) AS `papers in the by reviewing service`;


// AUTO TOPICS HIGHLIGHTS
MATCH
  (topics:SDAutoTopics)-->(a:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(entity:H_Entity)
  (topics)-->(highlighted:H_entity)
WITH DISTINCT
  topics,
  a,
  COLLECT(DISTINCT highlighted) AS highlighted_entities,
  COLLECT(DISTINCT entity) AS article_entities
WITH 
  topics,
  a,
  highlighted_entities,
  apoc.coll.intersection(highlighted_entities, article_entities) AS overlapping_highlihgts
UNWIND highlighted_entities AS highlighted_entity
UNWIND overlapping_highlights as overlapping_highlight
MERGE (col:VizCollection {name: "by-auto-topics"})
MERGE (subcol:VizSubCollection {name: topics.name})
MERGE (paper:VizPaper {doi: a.doi, pub_date: toString(DATETIME(a.pub_date))})
MERGE (col)-[:HasSubCol]->(subcol)
MERGE (subcol)-[:HasPaper]->(paper)
MERGE (highlight:VizEntity {text: highlighted_entity.name, category: 'topic_highlight'})
MERGE (subcol)-[:HasEntity]->(highlight)
MERGE (overlap:VizEntity {text: overlapping_highlight.name, category: 'paper_highlight'})
MERGE (paper)-[:HasEntity]->(overlap);
RETURN DISTINCT "done" AS `papers in the hypothesis set`;


// AUTOMAGIC
// find assays
MATCH (col:SDCollection)-[:has_article]->(a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "assay"})-[:Has_text]->(name:Term)
WHERE
  //a.doi = "10.1101/2020.06.29.178129" AND  // for testing
  (col.name = "covid19" OR col.name = "refereed-preprints") AND
  size(name.text) > 1  // exclude embarassing artefacts of the not so AI engine
WITH
  a, t, name
// link to entity network
MATCH
   (name)<-[:Has_text]-(bridge:H_Entity {category:"assay"})
//WHERE
//   bridge.concept_ext_ids <> ""
// find respective concept id
WITH
  a,
  name,
  COUNT(DISTINCT t) AS freq_in_this_paper,
  bridge.assay_concept_id AS concept_id,
  bridge.concept_name AS concept_name
WITH a, name, freq_in_this_paper, concept_id, concept_name
ORDER BY freq_in_this_paper DESC
// find most frequently used term in paper for each concept
WITH DISTINCT
// aggregate concepts with same name but different ids due to imperfect community detection
// RETURN  DISTINCT // for testing
  a, COLLECT(DISTINCT name.text)[0] AS name_in_this_paper, 
  SUM(freq_in_this_paper) AS aggregated_freq, 
  COLLECT(DISTINCT name.text) AS syn_in_this_paper, 
  COLLECT(DISTINCT concept_id) AS all_concept_id, 
  concept_name 
//cutoff to eliminate terms that map to a single concept and are only detected once
WHERE aggregated_freq > 1
// build viz graph
MERGE (paper:VizPaper {doi: a.doi, pub_date: toString(DATETIME(a.pub_date))})
MERGE (entity:VizEntity {text: name_in_this_paper, category: 'assay'})
MERGE (paper)-[:HasEntity]->(entity); 

// find entities
MATCH (col:SDCollection)-[:has_article]->(a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "entity"})-[:Has_text]->(name:Term)
WHERE
  (col.name = "covid19" OR col.name = "refereed-preprints") AND
  (size(name.text) > 1 OR toLower(name.text) = "s" ) // exclude embarassing artefacts of the not so AI engine but keep spike S SARS protein
WITH DISTINCT
  a, p, entity, name
//find synonyms
MATCH
   (name)<-[:Has_text]-(s:H_Entity {category: "entity"})
WHERE
  (s.type = entity.type) OR
  ((s.type = "gene" OR s.type = "protein" OR s.type = "geneprod") AND (entity.type = "gene" OR entity.type = "protein" OR entity.type = "geneprod"))
WITH
  a, p, entity, name, s
OPTIONAL MATCH (s)-[:Has_text]->(syn1:Term)
//combine synonyms
WITH DISTINCT
  a, entity, COUNT(DISTINCT p) AS N_panels, COLLECT(DISTINCT name) + COLLECT(DISTINCT syn1) AS all_synonyms
UNWIND all_synonyms AS syn
// remove duplicates
WITH DISTINCT
  a, entity, N_panels, syn
// use most popular synonym
ORDER BY syn.freq_in_panel DESC
WITH DISTINCT
  a, entity, N_panels, COLLECT(DISTINCT syn)[0] AS most_used
ORDER BY id(entity)
//collapse identical synonym groups
WITH DISTINCT
  a, COLLECT(DISTINCT entity.name)[0] AS representative_entity, SUM(N_panels) AS N, most_used
WHERE N > 2
WITH DISTINCT
  a, 
  COLLECT(DISTINCT representative_entity) AS entity_names, 
  COUNT(DISTINCT representative_entity) AS N_entities
//create info and entities for visualization

//BUT THIS CAN DANGLE WITHOUT ATTACHMENT TO COLLECTION
MERGE (paper:VizPaper {doi: a.doi, pub_date: toString(DATETIME(a.pub_date))})
WITH paper, entity_names
UNWIND entity_names AS text
MERGE (entity:VizEntity {text: text, category: "entity"})
MERGE (paper)-[:HasEntity]->(entity);

//sum of ranks for covid19 collection
// rank by assay
MATCH (col:SDCollection {name: "covid19"})-->(a:SDArticle)
WITH a
MATCH (viza:VizPaper)-[:HasEntity]->(entity:VizEntity {category: 'assay'})
WHERE
  viza.doi = a.doi
WITH
   viza, COUNT(DISTINCT entity) AS N_entities
ORDER BY N_entities DESC
WITH
  COLLECT(DISTINCT viza) as preprint_list
WITH 
  preprint_list, range(1, size(preprint_list)) AS ranks
UNWIND ranks as i
WITH
  COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_assay
// rank by entities
WITH
  ranked_by_assay
MATCH (col:SDCollection {name: "covid19"})-->(a:SDArticle)
WITH
  ranked_by_assay,
  a
MATCH (viza:VizPaper)-[:HasEntity]->(entity:VizEntity {category: 'entity'})
WHERE
  viza.doi = a.doi
WITH
  ranked_by_assay,
  viza, COUNT(DISTINCT entity) AS N_entities
ORDER BY N_entities DESC
WITH
  ranked_by_assay,
  COLLECT(DISTINCT viza) as preprint_list
WITH 
  ranked_by_assay,
  preprint_list, range(1, size(preprint_list)) AS ranks
UNWIND ranks as i
WITH
  ranked_by_assay,
  COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_entities
//Sum of ranks
WITH ranked_by_assay + ranked_by_entities AS ranked
UNWIND ranked as item //ranked by assay are listed first, ranked by biol entities second
WITH DISTINCT 
  item.preprint as preprint,
  SUM(item.rank) AS rank_sum,
  COLLECT(item.rank) AS ranks
WHERE size(ranks) = 2
WITH preprint, rank_sum
ORDER BY rank_sum ASC
LIMIT 20
MERGE (automagic:VizCollection {name: 'automagic'})
MERGE (covid19:VizSubCollection {name: 'covid19'})
MERGE (automagic)-[:HasSubCol]->(covid19)
MERGE (covid19)-[:HasPaper]->(preprint)
MERGE (preprint)-[:HasPaperRank]->(r:VizPaperRank {value: rank_sum, context: 'automagic'})
RETURN COUNT(preprint) AS `papers in the automagic set`;
