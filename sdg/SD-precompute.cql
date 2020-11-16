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


// HOT HYP

MATCH (coll:SDCollection)-->(a:SDArticle)-[r:HasH]->(h:Hypothesis)
WHERE
  // limit to automated collections and exclude manually curated PUBLICSEARCH from SourceData
  NOT coll.name = 'PUBLICSEARCH' AND 
  // start with 'hot' hypotheses
  h.is_hot AND 
  // only stuff that detected in 3 panels min
  r.n_panels > 2
WITH a, r.n_panels AS N_panels, h
ORDER BY N_panels DESC
// identify panels
MATCH
  (a)-->(f:SDFigure)-->(p:SDPanel),
  (p)-->(ict:CondTag {role: 'intervention'})-->(ih:H_Entity),
  (p)-->(act:CondTag {role: 'assayed'})-->(ah:H_Entity),
  (ih)-->(h)-->(ah)
// reformat panel into something usable for viz
// {id: id(p), title: f.fig_label + " (panel: " + p.panel_label + ")", text: p.caption, rank: f.fig_label + p.panel_label, panel_id: p.panel_id}
WITH DISTINCT a, ah, ih, N_panels, {id: id(p), title: f.fig_label + " (panel: " + p.panel_label + ")", text: p.caption, rank: f.fig_label + p.panel_label} AS reformatted_panel
// aggregate relevant panels
WITH a, COLLECT(DISTINCT reformatted_panel) AS panel_group, N_panels, ih, ah
MATCH (a)-->(:SDFigure)-->(:SDPanel)-->(:CondTag)-->(assay:H_Entity {category: "assay"})
// take only papers with some experimental assay detected, aggregated by pseudo synonyms
WITH DISTINCT a, panel_group, N_panels, ih, ah, COUNT(DISTINCT assay.concept_name) AS N_assay
WHERE N_assay > 3
WITH DISTINCT a, panel_group, N_panels, ih, ah, N_assay
ORDER BY
  a.pub_date DESC,
  N_panels DESC
WITH DISTINCT COLLECT({article: a, panels: panel_group}) AS article_with_panels, ih, ah
// limit to 20 hyp
LIMIT 20
// generate ordered id
WITH COLLECT(DISTINCT {article_with_panels: article_with_panels, ctrl_v: ih, meas_v: ah}) AS all
UNWIND range(0, size(all)-1) as i

///////////////////////////////GENERATE PRECOMPUTED VIZ GRAPH///////////////////////////////
// unpack it all to create the viz graph
WITH i, all[i].article_with_panels as article_with_panels, all[i].ctrl_v AS ctrl_v, all[i].meas_v AS meas_v
UNWIND article_with_panels as item
WITH item.article.doi AS doi, item.article.pub_date AS pub_date, item.panels AS panels, ctrl_v.name AS ctrl_v_text, meas_v.name AS meas_v_text
UNWIND panels AS panel
WITH 
  doi, pub_date, ctrl_v_text, meas_v_text,
  panel.title AS info_title, panel.text AS info_text, panel.rank AS info_rank, panel.entities as entities
// id; will need to have constraint on id + query
MERGE (col:VizCollection {name: "by_hyp"})
MERGE (subcol:VizSubCollection {name: "hyp_" + ctrl_v_text + ' --> ' + 'meas_v_text'})
MERGE (paper:VizPaper {doi: doi, pub_date: toString(DATETIME(pub_date))})
MERGE (col)-[:HasSubCol]->(subcol)
MERGE (subcol)-[:HasPaper]->(paper)
MERGE (info:VizInfo {doi: doi, title: info_title, text: info_text, rank: info_rank, info_type: "panel-caption"}) // avoid probelms with NULL and MERGE
MERGE (paper)-[:HasInfo]->(info)
MERGE (c:VizEntity {text: ctrl_v_text, role: "controlled_variable"})
MERGE (m:VizEntity {text: meas_v_text, role: "measured_variable"})
MERGE (c)-[:HasPotentialEffectOn]->(m)
MERGE (subcol)-[:HasEntity]->(c)
MERGE (subcol)-[:HasEntity]->(m)
RETURN DISTINCT "done" AS `papers in the hypothesis set`;


// BY HYP ON COVID-19

///////////////////////////////EXCLUSION LIST///////////////////////////////
//Exclusion list based on SourceData normalized entities
// MATCH (syn:Term)<--(entity:H_Entity)<--(ct:CondTag)
// WHERE 
//   entity.ext_ids <> ""
// WITH DISTINCT entity.name AS name, COLLECT(DISTINCT syn.text) AS synonyms, COLLECT(DISTINCT ct) AS cts, 1.0*COUNT(DISTINCT ct) AS N
// UNWIND cts as ct
// WITH DISTINCT name, synonyms, N, ct.role as role, 1.0*COUNT(DISTINCT ct) AS N_role
// WITH name, synonyms, role, N, N_role, 100.0*(N_role / N) AS fract
// ORDER BY N DESC, fract DESC
// WITH name, synonyms, N, COLLECT(role)[0] AS dominant_role, COLLECT(fract)[0] AS dom_fract
// WHERE 
//   (dominant_role = "normalizing" OR dominant_role = "reporter" OR dominant_role = "component")
//   AND
//   dom_fract > 75 AND N > 10.0
// WITH COLLECT(name) + synonyms AS all
// UNWIND all as terms
// WITH COLLECT(DISTINCT terms) AS exclusion_list

// ///////////////////////////////CHOOSE SD CURATED FIRST///////////////////////////////
// //prioritize manually curated papers
// //MATCH (a:SDArticle)
// //WHERE toLower(a.journalName) IN ["biorxiv", "medrxiv"]
// //WITH a, exclusion_list
// //ORDER BY a.source DESC // manually curated source = 'sdapi' sorted before automatic papers where source = 'eebapi'
// //WITH DISTINCT a.doi AS doi, COLLECT(a) AS same_paper, exclusion_list
// //WITH same_paper[0] as a, exclusion_list

// ///////////////////////////////IDENTIFY HYPOTHESES//////////////////////////////////
// // identify hypotheses as intervention - assayed pairs
// MATCH
//   (col:SDCollection {name:"covid19"})-[:has_article]->(a:SDArticle)-->(f:SDFigure)-->(p:SDPanel),
//   path_1=(p)-->(i:CondTag {role: "intervention"})-->(ctrl:H_Entity)-->(ctrl_term:Term),
//   path_2=(p)-->(m:CondTag {role: "assayed"})-->(meas:H_Entity)-->(meas_term:Term)
// WHERE
//   // trying to avoid trivial same - same pairs (eg typical for siRNA control exp)
//   ctrl.name <> meas.name // could still be 2 entities normalized differently
//   AND
//   // exclude terms that are in the exclusion list
//   NONE (n IN nodes(path_1) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
//   AND
//   NONE (n IN nodes(path_2) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
//   AND
//   // eliminate figure and panels without a caption or label such as graphical abstracts etc
//   EXISTS(f.fig_label) AND EXISTS(p.panel_label)
  
// // make sure figures are ordered by label
// WITH DISTINCT
//     a, f, p, ctrl, meas
// ORDER BY 
//   f.fig_label ASC, p.panel_label ASC,
//   id(ctrl) ASC, id(meas) ASC // deterministic order to faciliate aggregation later
// // aggregate panels to count how many panels have same hypothesis
// WITH DISTINCT
//     a, 
//     // capture relevant info (fig_label) in the format neededed for REST and 
//     // we need to do it now rather than later because figure-level info is still available at this stage
//     COLLECT(DISTINCT {id: id(p), title: f.fig_label + " (panel: " + p.panel_label + ")", text: p.caption, rank: f.fig_label + p.panel_label, panel_id: p.panel_id}) AS panel_group, // will need to generate position_idx from sdapi
//     COUNT(DISTINCT p) AS N_panels,
//     ctrl.name AS ctrl_name, 
//     meas.name AS meas_name
// ORDER BY ctrl_name, meas_name
// WHERE N_panels > 2 // keep only hypotheses identified in more than one experiment
// // agreggate hypothesis elements shared across the group of panels
// WITH a, panel_group, N_panels, COLLECT(DISTINCT ctrl_name) AS ctrl_v, COLLECT(DISTINCT meas_name) AS meas_v
// // crudly prioritize experimental papers with at least 3 identified assays
// MATCH (a)-->(:SDFigure)-->(:SDPanel)-->(:CondTag)-->(assay:H_Entity {category: "assay"})
// WITH DISTINCT a, panel_group, N_panels, {ctrl_v: ctrl_v, meas_v: meas_v} AS hyp, COUNT(DISTINCT assay) AS N_assay
// ORDER BY
//   a.pub_date DESC,
//   N_panels DESC
// // select the hypotheses detected in the most panels as the dominant hypothesis. Could keep the top 5 instead?
// WITH a, COLLECT(panel_group)[0] AS selected_panels, COLLECT(hyp)[0] AS dominant, N_assay
// WHERE N_assay > 3
// // most recent first
// WITH a, selected_panels, dominant, N_assay
// // recover all entities associated with the selected panels for manually curated papers
// UNWIND selected_panels AS selected_panel
// MATCH (p:SDPanel)-->(ct:CondTag)
// WHERE selected_panel.id= id(p)
// WITH DISTINCT a, selected_panel, COLLECT(DISTINCT ct{.*, source: p.source}) as entities, dominant, N_assay
// // repackage entities with the respective panels for subsequent display
// WITH DISTINCT a, COLLECT(DISTINCT selected_panel{.*, entities: entities}) AS selected_panels, dominant, N_assay
// // assign an id to each hypothesis group
// WITH dominant, COLLECT({doi: a.doi, info: selected_panels, pub_date: a.pub_date}) AS papers
// // limit to most recent 20 hyp
// LIMIT 20
// // generate ordered id
// WITH COLLECT([dominant, papers]) AS all_results
// UNWIND range(0, size(all_results)-1) as id

// ///////////////////////////////GENERATE PRECOMPUTED VIZ GRAPH///////////////////////////////
// // unpack it all to create the viz graph
// WITH id, all_results[id][0] as hyp, all_results[id][1] as papers
// UNWIND papers as paper
// WITH id, hyp, paper.doi AS doi, paper.info AS info, paper.pub_date AS pub_date
// UNWIND info AS info_item
// WITH 
//   id, hyp, doi, pub_date, 
//   info_item.title AS info_title, info_item.text AS info_text, info_item.rank AS info_rank, info_item.entities as entities, info_item.panel_id AS info_id
// // id; will need to have constraint on id + query
// UNWIND hyp.ctrl_v AS ctrl_v // string
// UNWIND hyp.meas_v AS meas_v // string
// UNWIND entities as entity // THIS IS KILLING IT IF entities == []
// MERGE (col:VizCollection {name: "by_hyp"})
// MERGE (subcol:VizSubCollection {name: "hyp_" + toString(id)})
// MERGE (paper:VizPaper {doi: doi, pub_date: toString(DATETIME(pub_date))})
// MERGE (col)-[:HasSubCol]->(subcol)
// MERGE (subcol)-[:HasPaper]->(paper)
// MERGE (info:VizInfo {doi: doi, title: info_title, text: info_text, rank: info_rank, id: info_id, info_type: "panel-caption"}) // avoid probelms with NULL and MERGE
// MERGE (paper)-[:HasInfo]->(info)
// MERGE (c:VizEntity {text: ctrl_v, role: "controlled_variable"})
// MERGE (m:VizEntity {text: meas_v, role: "measured_variable"})
// MERGE (c)-[:HasPotentialEffectOn]->(m)
// MERGE (subcol)-[:HasEntity]->(c)
// MERGE (subcol)-[:HasEntity]->(m)
// RETURN DISTINCT "done" AS `papers in the hypothesis set`;


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
