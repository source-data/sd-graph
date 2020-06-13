// PRECOMPUTE RESULTS

// PURGE PRECOMPUTED
MATCH (n:VizPaper)-[r]-() DELETE r;
MATCH (n:VizInfo)-[r]-() DELETE r;
MATCH (n:VizPaper) DELETE n;
MATCH (n:VizInfo) DELETE n;
MATCH (n:VizEntity)-[r]-() DELETE r;
MATCH (n:VizEntity) DELETE n;


// BY REVIEWING SERVICE

UNWIND ['review commons', 'embo press', 'elife'] AS reviewing
MATCH (a:Article)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review {reviewed_by: reviewing})
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: reviewing})
WITH DISTINCT
    reviewing, a, review, annot
WHERE 
    EXISTS(review.text) OR EXISTS(annot.text)
WITH reviewing, a, review, annot, a.version AS version
ORDER BY version DESC
// keep only the most recent version of the article
WITH reviewing, COLLECT(DISTINCT a)[0] AS most_recent, review, annot
// get the figures
MATCH (most_recent)-->(f:Fig)
// eliminate figures without a caption such as graphical abstracts etc
WHERE EXISTS(f.caption)
WITH DISTINCT
    reviewing, most_recent.doi AS doi, most_recent.publication_date AS pub_date, review, annot,
    f.label AS fig_label, f.caption AS caption, f.position_idx AS position_idx, f
ORDER BY
    pub_date DESC, position_idx ASC
WITH DISTINCT
   reviewing, doi, pub_date, fig_label, caption, position_idx
MERGE (paper:VizPaper {id:reviewing, doi: doi, query:"by_reviewing_service", pub_date: pub_date, rank: pub_date})
MERGE (paper)-[:HasInfo]->(info:VizInfo {title: fig_label, text: caption, rank: position_idx})
//RETURN paper, info;
RETURN COUNT(DISTINCT paper) AS `papers in the by reviewing service`;



// BY HYP

///////////////////////////////EXCLUSION LIST///////////////////////////////
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

///////////////////////////////CHOOSE SD CURATED FIRST///////////////////////////////
//prioritize manually curated papers
MATCH (a:SDArticle)
WHERE toLower(a.journalName) IN ["biorxiv", "medrxiv"]
WITH a, exclusion_list
ORDER BY a.source DESC // manually curated source = 'sdapi' sorted before automatic papers where source = 'eebapi'
WITH DISTINCT a.doi AS doi, COLLECT(a) AS same_paper, exclusion_list
WITH same_paper[0] as a, exclusion_list

///////////////////////////////IDENTIFY HYPOTHESES//////////////////////////////////
// identify hypotheses as intervention - assayed pairs
MATCH
  (a)-->(f:SDFigure)-->(p:SDPanel),
  path_1=(p)-->(i:CondTag {role: "intervention"})-->(ctrl:H_Entity)-->(ctrl_term:Term),
  path_2=(p)-->(m:CondTag {role: "assayed"})-->(meas:H_Entity)-->(meas_term:Term)
WHERE
  // trying to avoid trivial same - same pairs (eg typical for siRNA control exp)
  ctrl.name <> meas.name // could still be 2 entities normalized differently
  AND
  // exclude terms that are in the exclusion list
  NONE (n IN nodes(path_1) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
  AND
  NONE (n IN nodes(path_2) WHERE labels(n)=['Term'] AND (n.text IN exclusion_list))
// make sure figures are ordered by label
WITH DISTINCT
    a, f, p, 
    ctrl.name AS ctrl_name, 
    meas.name AS meas_name
ORDER BY f.fig_label ASC, p.panel_label ASC
// aggregate panels to count how many panels have same hypothesis
WITH DISTINCT
    a, 
    // capture relevant info (fig_label) in the format neededed for REST and 
    // we need to do it now rather than later because figure-level info is still available at this stage
    COLLECT(DISTINCT {id: id(p), title: f.fig_label, text: p.caption, rank: p.panel_label}) AS panel_group,
    COUNT(DISTINCT p) AS N_panels,
    ctrl_name, meas_name
ORDER BY ctrl_name, meas_name //deterministic order
WHERE N_panels > 1 // keep only hypotheses identified in more than one experiment
// agreggate hypothesis elements shared across the group of panels
WITH a, panel_group, N_panels, COLLECT(DISTINCT ctrl_name) AS ctrl_v, COLLECT(DISTINCT meas_name) AS meas_v
// crudly prioritize experimental papers with at least 3 identified assays
MATCH (a)-->(:SDFigure)-->(:SDPanel)-->(:CondTag)-->(assay:H_Entity {category: "assay"})
WITH DISTINCT a, panel_group, N_panels, {ctrl_v: ctrl_v, meas_v: meas_v} AS hyp, COUNT(DISTINCT assay) AS N_assay
ORDER BY N_panels DESC, a.pub_date DESC
// select the hypotheses detected in the most panels as the dominant hypothesis. Could keep the top 5 instead?
WITH a, COLLECT(panel_group)[0] AS selected_panels, COLLECT(hyp)[0] AS dominant, N_assay
WHERE N_assay > 3 // move up?
WITH a, selected_panels, dominant, N_assay
LIMIT 20
// assign an id to each hypothesis group
WITH dominant, COLLECT({doi: a.doi, info: selected_panels, pub_date: a.pub_date, rank: N_assay}) AS papers
WITH COLLECT([dominant, papers]) AS all_results
UNWIND range(0, size(all_results)-1) as id

///////////////////////////////GENERATE PRECOMPUTED VIZ GRAPH///////////////////////////////
// unpack it all to create the viz graph
WITH id, all_results[id][0] as hyp, all_results[id][1] as papers
UNWIND papers as paper
WITH id, hyp, paper.doi AS doi, paper.rank AS paper_rank, paper.info AS info, paper.pub_date AS pub_date
UNWIND info AS info_item
WITH 
  id, hyp, doi, pub_date, paper_rank, 
  info_item.title AS info_title, info_item.text AS info_text, info_item.rank AS info_rank
// id; will need to have constraint on id + query
UNWIND hyp.ctrl_v AS ctrl_v
UNWIND hyp.meas_v AS meas_v
MERGE (paper:VizPaper {id: id, doi:doi, query: "by_hyp", pub_date: pub_date, rank: paper_rank})
MERGE (paper)-[:HasInfo]->(info:VizInfo {title: info_title, text: info_text, rank: info_rank})
MERGE (c:VizEntity {text: ctrl_v})-[:HasPotentialEffectOn]->(m:VizEntity {text: meas_v})
MERGE (paper)-[:HasEntity]->(c)
MERGE (paper)-[:HasEntity]->(m)
// diplay viz graph
//RETURN paper, info, c, m;
RETURN COUNT(DISTINCT paper) AS `papers in the by hypothesis set`;



// AUTOMAGIC
// find entities
MATCH (a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "assay"})-[:Has_text]->(name:Term)
WITH
  a, entity, name
//find synonyms
MATCH
   (name)<-[:Has_text]-(bridge:H_Entity {category:"assay"})
WITH a, entity, name, bridge
OPTIONAL MATCH
    (bridge)-[:Has_text]->(syn1:Term)
//combine synonyms
WITH DISTINCT a, entity, COLLECT(name) + COLLECT(syn1) AS all_synonyms
UNWIND all_synonyms AS syn
// remove duplicates
WITH DISTINCT a, entity, syn
// rank synonym by popularity
ORDER BY syn.freq_in_panel DESC
WITH DISTINCT a, entity, COLLECT(DISTINCT syn)[0] AS most_used
ORDER BY id(entity)
//collapse identical synonym groups
WITH DISTINCT a, COLLECT(DISTINCT entity.name)[0] AS representative_entity, most_used
WITH DISTINCT a, COLLECT(DISTINCT representative_entity) AS entities, COUNT(DISTINCT representative_entity) AS N_entities
ORDER BY N_entities DESC
WITH COLLECT(DISTINCT {title: a.title, doi: a.doi, source:a.source, entities: entities, pub_date: a.pub_date, N_entities: N_entities}) as preprint_list
WITH preprint_list, range(1, size(preprint_list)) AS ranks
UNWIND ranks as i
WITH COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_assay

///////////////////////PART B: RANK BY NUMBER OF ENTITIES///////////////////////////////

//start with only most recent version
//MATCH (preprint:SDArticle {journalName: "biorxiv"})
//WITH preprint, ranked_by_assay
//ORDER BY preprint.version DESC
//WITH DISTINCT preprint.doi AS doi, COLLECT(DISTINCT preprint)[0] AS a, ranked_by_assay //keep only the most recent

// find entities
MATCH (a:SDArticle {journalName: "biorxiv"})-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity {category: "entity"})-[:Has_text]->(name:Term)
WITH DISTINCT
  ranked_by_assay,
  a, p, entity, name
//find synonyms
MATCH
   (name)<-[:Has_text]-(s:H_Entity {category:"entity"})
WHERE
  (s.type = entity.type) OR
  ((s.type = "gene" OR s.type = "protein" OR s.type = "geneprod") AND (entity.type = "gene" OR entity.type = "protein" OR entity.type = "geneprod"))
WITH
  ranked_by_assay,
  a, p, entity, name, s
OPTIONAL MATCH (s)-[:Has_text]->(syn1:Term)
WHERE syn1 <> name
//combine synonyms
WITH DISTINCT
  ranked_by_assay,
  a, entity, COUNT(DISTINCT p) AS N_panels, COLLECT(DISTINCT name) + COLLECT(DISTINCT syn1) AS all_synonyms
UNWIND all_synonyms AS syn
// remove duplicates
WITH DISTINCT
  ranked_by_assay,
  a, entity, N_panels, syn
// use most popular synonym
ORDER BY syn.freq_in_panel DESC
WITH DISTINCT
  ranked_by_assay,
  a, entity, N_panels, COLLECT(DISTINCT syn)[0] AS most_used
ORDER BY id(entity)
//collapse identical synonym groups
WITH DISTINCT
  ranked_by_assay,
  a, COLLECT(DISTINCT entity.name)[0] AS representative_entity, SUM(N_panels) AS N, most_used
WHERE N > 2
WITH DISTINCT
  ranked_by_assay,
  a, 
  COLLECT(DISTINCT representative_entity) AS entities, 
  COUNT(DISTINCT representative_entity) AS N_entities
ORDER BY N_entities DESC
WITH
  ranked_by_assay,
  COLLECT(DISTINCT {title: a.title, doi: a.doi, source:a.source, entities: entities, pub_date: a.pub_date, N_entities: N_entities}) as preprint_list
WITH 
  ranked_by_assay,
  preprint_list, range(1, size(preprint_list)) AS ranks
UNWIND ranks as i
WITH
  ranked_by_assay,
  COLLECT({rank: i, preprint: preprint_list[i-1]}) AS ranked_by_entities

///////////////////////PART C: RETURN BY SUM OF RANKS///////////////////////////////
//sum of ranks
WHERE (ranked_by_entities <> []) AND (ranked_by_assay <> [])
WITH ranked_by_assay + ranked_by_entities AS ranked
UNWIND ranked as item //ranked by assay are listed first, ranked by biol entities second
WITH DISTINCT 
  item.preprint.doi as doi,
  item.preprint.pub_date AS pub_date,
  COLLECT(DISTINCT item.preprint.entities) AS entities, // list of assays first, list of biol entities second
  SUM(item.rank) AS rank_sum,
  COLLECT(item.rank) AS ranks
WHERE size(ranks)=2
WITH 
  doi, pub_date, entities[0] AS exp_assays, entities[1] AS bio_entities, rank_sum      
ORDER BY rank_sum ASC
LIMIT 10
// unpack
MERGE (paper:VizPaper {id: 'automagic', doi: doi, query:'automagic', pub_date: pub_date, rank: rank_sum})
MERGE (paper)-[:HasInfo]->(info_2:VizInfo {title: 'Experimental approaches' , text: exp_assays, rank: "0"})
MERGE (paper)-[:HasInfo]->(info_1:VizInfo {title: 'Biological entities' , text: bio_entities, rank: "1"})
WITH paper, info_1, info_2, bio_entities, exp_assays
UNWIND bio_entities AS text_1
MERGE (info_1)-[:HasEntity]->(item_1:VizEntity {text: text_1})
WITH paper, info_1, info_2, item_1, exp_assays
UNWIND exp_assays AS text_2
MERGE (info_2)-[:HasEntity]->(item_2:VizEntity {text: text_2})
//RETURN paper, info_1, info_2, item_1, item_2;
RETURN COUNT(DISTINCT paper) AS `papers in the automagic set`;