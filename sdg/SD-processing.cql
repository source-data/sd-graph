/////PROCESSING THE GRAPH//////


CREATE CONSTRAINT h_entity_id IF NOT EXISTS ON (h:H_Entity) ASSERT h.combo_id IS UNIQUE;
//CREATE CONSTRAINT ON (h:H_Entity) ASSERT (h.ext_id, h.type, h.category, h.name) IS NODE KEY; //only neo4j Enterprise!
CREATE CONSTRAINT term_text_ IF NOT EXISTS ON (te:Term) ASSERT te.text IS UNIQUE;

// purge processed nodes
// prelimin solution before proper combined keys are implemented that will allow using MERGE instead of CREATE cond Tags

MATCH (ct:CondTag)-[r]-()
DETACH DELETE ct
RETURN COUNT(DISTINCT ct) AS `deleted CondTag`;

MATCH (ct:CondTag)
RETURN COUNT(ct) AS `remaining CondTag`;

MATCH (h:H_Entity)-[r]-()
DETACH DELETE h
RETURN COUNT(DISTINCT h) AS `deleted H_Entity`;

MATCH (h:H_Entity)
RETURN COUNT(h) AS `remaining H_Entity`;

MATCH (t:Term)
DETACH DELETE t
RETURN COUNT(DISTINCT t) AS `deleted Term`;

MATCH (t:Term)
RETURN COUNT(t) AS `remaining Term`;


//journal name to lower case
MATCH (a:SDArticle)
SET a.journalName = toLower(a.journalName);

//trim and tolower text
MATCH(t:SDTag)
SET t.norm_text = toLower(trim(t.text));

//add text if none there
MATCH(t:SDTag)
WHERE t.text = ""
SET t.text = toLower(t.ext_names)
RETURN COUNT(t) AS `added ext_names instead of emtpy text tag`;

//remove sick tags with no name and no ext_names
MATCH(t:SDTag)-[r]-()
WHERE t.text = "" AND t.ext_names = ""
DELETE r, t
RETURN COUNT(t) AS `deleted empty tags`;

//replace NULL by "" for consistency 
MATCH(t:SDTag)
WHERE
    t.ext_names IS NULL
SET t.ext_names = ""
RETURN COUNT(t) AS `ext name NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.ext_ids IS NULL
SET t.ext_ids = ""
RETURN COUNT(t) AS `ext ids NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.ext_dbs IS NULL
SET t.ext_dbs = ""
RETURN COUNT(t) AS `ext_dbs NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.type IS NULL
SET t.type = ""
RETURN COUNT(t) AS `type NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.role IS NULL
SET t.role = ""
RETURN COUNT(t) AS `role NULL into ""`;

MATCH(f:Fig)
WHERE NOT EXISTS(f.position_idx)
SET  f.position_idx = ""
RETURN COUNT(f) AS `NULL fig position_idx set to ""`;

MATCH(p:SDPanel)
WHERE p.panel_id IS NULL
SET p.panel_id = ""
RETURN COUNT(p) AS `NULL panel_id set to ""`;


//A: condense tags with same ext id and role
MATCH (p:SDPanel)-->(t:SDTag)
WHERE
    t.ext_ids <> ""
WITH DISTINCT p, t.role AS role, t.type as type, t.category as category, t.ext_ids AS ext_ids, COLLECT(DISTINCT (t.norm_text)) AS text, COUNT(DISTINCT t) AS N
ORDER BY N DESC
WITH DISTINCT p, role, type, category, ext_ids, text[0] AS most_used_text
CREATE (c:CondTag {role: role, type: type, category: category, ext_ids: ext_ids, text: most_used_text})
CREATE (p)-[rel:HasCondTag]->(c);

MATCH 
   (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
WHERE
    t.role = c.role AND t.ext_ids = c.ext_ids AND t.type = c.type
WITH DISTINCT t, c
CREATE (t)-[:Condensed_into]->(c)
RETURN COUNT(c)  AS `condensed tags`;


//B: condense tags that have no ext_ids but same text and same type and role
MATCH (p:SDPanel)-->(t:SDTag)
WHERE
    t.ext_ids = "" AND
    (t.category <> "" OR t.type <> "")
WITH DISTINCT p, t.norm_text AS text, t.role AS role, t.type AS type, t.category AS category
CREATE (c:CondTag {role: role, type:type, category: category, ext_ids: "", text: text})
CREATE (p)-[:HasCondTag]->(c);

MATCH 
    (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
WHERE
    c.ext_ids = "" AND t.ext_ids = "" AND
    t.role = c.role AND t.type = c.type AND t.category = c.category AND t.norm_text = c.text
WITH DISTINCT t, c
CREATE (t)-[:Condensed_into]->(c)
RETURN COUNT(c) AS `condensed tags`;


// Confirm that no SDTag is linked to multiple CondTag
MATCH (t:SDTag)-[r:Condensed_into]->(ct:CondTag)
WITH t, COUNT(DISTINCT ct) AS N
WHERE N > 1
RETURN COUNT(t) AS `SDTag associated with multiple CondTag`;


// Confirm that all CondTag have a non-empty text property
MATCH (ct:CondTag)
WHERE ct.text = "" OR ct.text IS NULL
RETURN COUNT(ct) AS `CondTag with no text`;


//A: Create hybrid entities from CondTag with ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids <> ""
WITH DISTINCT split(ct.ext_ids,'///') as ids, ct.type AS type, ct.text AS text, ct.category AS category, ct
UNWIND ids AS id
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + id})
ON CREATE SET hyb.ext_ids = id, hyb.type = type, hyb.category = category, hyb.name = text
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities with ext_ids`;


//B: Create hybrid entities from CondTag without an ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids = ""
WITH ct.text AS text, ct.type AS type, ct.category AS category, ct
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + text})
ON CREATE SET hyb.ext_ids = "", hyb.type = type, hyb.category = category, hyb.name = text 
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities without ext_ids`;


//report H_Entity with no names
MATCH (h:H_Entity)
WHERE 
    h.name = ""
RETURN COUNT(h) AS `H_Entity remaining without a name`;


//Create unique terms
MATCH (t:SDTag)-->(c:CondTag)-->(hyb:H_Entity)
WITH DISTINCT t.norm_text AS text, hyb
MERGE (te:Term {text: text})
MERGE (hyb)-[r:Has_text]->(te)
RETURN COUNT(r) AS `unique terms`;

// Compute popularity of terms
MATCH (sd:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity)-->(t:Term)
WITH t, COUNT(DISTINCT p) AS freq
SET t.freq_in_panel = freq
RETURN COUNT (t) as `tags with popularity frequency added`;


//infer tested hypotheses at condensed tag level
MATCH 
  (p:SDPanel)-->(intervention:CondTag {role: "intervention"}),
  (p:SDPanel)-->(assayed:CondTag {role: "assayed"})
MERGE (intervention)-[r:H]->(assayed)
RETURN COUNT(r) AS `hypotheses at cond tag level`;

// quasi synonyms
// H_Entity - Term - H_Entity network for quasi-synonyms
MATCH
  (entity_1:H_Entity)-[:Has_text]->(bridge:Term)<-[:Has_text]-(entity_2:H_Entity)
WHERE
  entity_1 <> entity_2 AND
    entity_1.category = "assay" AND entity_2.category = "assay"
MERGE
  (entity_1)-[r:related_concept]-(entity_2)
RETURN
  COUNT(r);


// COMMUNITY DETECTION FOR PSEUDO SYNONYMS
MATCH (h:H_Entity) SET h.assay_concept_id = Null;
CALL gds.louvain.write(
  {
    nodeQuery: 'MATCH (h:H_Entity {category: "assay"}) RETURN id(h) AS id',
    relationshipQuery: 'MATCH (h1:H_Entity {category: "assay"})-[:related_concept]-(h2:H_Entity {category: "assay"}) RETURN id(h1) AS source, id(h2) AS target',
    writeProperty: 'assay_concept_id'
  }
);

// adding cluster name
MATCH (entity:H_Entity {category: "assay"})-[:Has_text]->(te:Term)
WITH entity, COUNT(DISTINCT te) AS entity_popularity
ORDER BY entity_popularity DESC
WITH
  entity.assay_concept_id AS concept_id, 
  COUNT(DISTINCT entity) AS size, 
  COLLECT(entity)[0] AS most_popular_entity, 
  COLLECT(DISTINCT entity) AS cluster
UNWIND cluster AS entity
SET entity.concept_name = most_popular_entity.name, entity.concept_ext_ids = most_popular_entity.ext_ids
RETURN DISTINCT 
  // most_popular_entity.concept_name,
  // most_popular_entity.concept_ext_ids,
  // concept_id, size, 
  COUNT(DISTINCT entity.assay_concept_id) AS `clusters of assay related concepts`;


//copy publication date and abstract from jats articles to SDArticles
MATCH (jats:Article), (a:SDArticle)
WHERE jats.doi = a.doi
WITH DISTINCT 
  jats.doi AS doi, 
  jats.publication_date AS pub_date, 
  jats.abstract AS abstract, 
  a
ORDER BY pub_date DESC // most recent first
WITH DISTINCT doi, COLLECT(pub_date)[0] AS most_recent, COLLECT(abstract)[0] AS abstr, a
SET a += {pub_date: most_recent, abstract: abstr}
RETURN COUNT(DISTINCT a);

//Link to authors via Contrib nodes
MATCH (jats:Article), (sd:SDArticle)
WHERE jats.doi = sd.doi
WITH DISTINCT
  sd.doi AS doi,
  sd,
  jats
ORDER BY jats.publication_date DESC
WITH DISTINCT
  doi,
  sd,
  COLLECT(jats)[0] AS most_recent
MATCH
  (most_recent)-[:has_author]->(au:Contrib)
WITH DISTINCT
  doi,
  sd,
  au
MERGE (sd)-[r:has_author]->(au)
RETURN COUNT(DISTINCT r) AS N_auth_relationships;


//create hypotheses summaries at paper level
MATCH 
  (art:SDArticle)-->(f1:SDFigure)-->(p1:SDPanel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
  (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
// RETURN art,ih,ah,COLLECT(f1),COLLECT(p1),COLLECT(i1),COLLECT(a1),COUNT(DISTINCT p1) AS N_p,COUNT(DISTINCT f1) AS N_f ORDER BY N_p DESC LIMIT 1
WITH art,ih,ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
  MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
  MERGE (art)-[:HasH {n_panels:N_p,n_figures:N_f}]->(h)
RETURN COUNT(DISTINCT h) AS `hypotheses at paper level`;


// add text descr to hypothesis
MATCH (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity) 
SET h.description = ih.name + " --> " + ah.name;


// flag possible self-test hypotheses
MATCH (h:Hypothesis) SET h.self_test = False;
MATCH
  (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity),
  (ih)-->(same:Term)
WITH h, ah, same
MATCH (ah)-->(same)
SET h.self_test = True
RETURN COUNT(DISTINCT h) AS `flagged self-test hypotheses`;


// Flag possible boring entities, helpful to filter them later
// Exclusion list based on SourceData normalized and reporter entities
MATCH (h:H_Entity) SET h.boring = False;
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
  (dominant_role = "normalizing" OR dominant_role = "reporter")
  AND
  dom_fract > 75 AND N > 10.0
WITH COLLECT(name) + synonyms AS all
UNWIND all as terms
WITH COLLECT(DISTINCT terms) AS exclusion_list
UNWIND exclusion_list AS excluded_term
MATCH (h:H_Entity)-->(te:Term {text: excluded_term})
SET h.boring = True;


//Add weight to hypotheses nodes
MATCH (a:SDArticle)-[h:HasH]->(hyp:Hypothesis)
WITH 
  hyp, 
  SUM(DISTINCT h.n_panels) AS sum_n_panels, 
  SUM(DISTINCT h.n_figures) AS sum_n_figures, 
  COUNT(DISTINCT a) AS n_articles
SET 
  hyp.n_panels = sum_n_panels,
  hyp.n_figures = sum_n_figures,
  hyp.n_articles = n_articles
RETURN DISTINCT "added weights to hypotheses nodes";


// hypothesis-as-node network
MATCH
  (up:H_Entity)-[:Is_Intervention_of]->(h1:Hypothesis)-[:Has_Assayed]->(ah:H_Entity)-[:Is_Intervention_of]->(h2:Hypothesis)-[:Has_Assayed]->(do:H_Entity)
WHERE (NOT up.boring) AND (NOT ah.boring) AND (NOT do.boring)
MERGE (h1)-[chain:hyp_chain]->(h2)
RETURN COUNT(DISTINCT chain) AS `hypothesis chains`;


// hypothesis-as-edge network
MATCH
  (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity)
WHERE (NOT ih.boring) AND (NOT ah.boring)
MERGE (ih)-[tested:Tested]->(ah)
RETURN COUNT(tested) AS `hypotheses at entity level`;


//transfer hypothesis weight to :Tested links
MATCH (i:H_Entity)-->(h:Hypothesis)-->(a:H_Entity), (i)-[r:Tested]->(a)
SET
  r.n_panels = h.n_panels,
  r.n_figures = h.n_figures,
  r.n_articles = h.n_articles
RETURN DISTINCT "transferred hypothesis weight to :Tested links";


//add scale to entities

//MATCH (e:H_Entity {type:"molecule"}) SET e.scale = 1;
//MATCH (e:H_Entity {type:"gene"}) SET e.scale = 2;
//MATCH (e:H_Entity {type:"protein"}) SET e.scale = 2;
//MATCH (e:H_Entity {type:"subcellular"}) SET e.scale = 3;
//MATCH (e:H_Entity {type:"cell"}) SET e.scale = 4;
//MATCH (e:H_Entity {type:"tissue"}) SET e.scale = 5;
//MATCH (e:H_Entity {type:"organism"}) SET e.scale = 6;
//RETURN "added scales to entities";

// resolver nodes to map resource to base url and possibly to id regex pattern (according to identifiers.org)
// need to provide a recipe to transform in to compact identifier and just use identifiers.org
// MERGE(:Resolver {name: "NCBI gene", url: "http://www.ncbi.nlm.nih.gov/gene/"}); // 59272
// MERGE(:Resolver {name: "NCBI taxon", url: "http://www.ncbi.nlm.nih.gov/taxonomy/"}); // 10090
// MERGE(:Resolver {name: "OBI", url: "https://bioportal.bioontology.org/ontologies/OBI/?p=classes&conceptid=http://purl.obolibrary.org/obo/", about: "http://purl.obolibrary.org/obo/"}); // OBI_0000445
// MERGE(:Resolver {name: "Uberon", url: "http://purl.bioontology.org/ontology/UBERON/"}); // UBERON:0000955
// MERGE(:Resolver {name: "CVCL", url: "https://identifiers.org/cellosaurus:"}); // CVCL_0574
// MERGE(:Resolver {name: "BAO", url: "http://bioportal.bioontology.org/ontologies/BAO/bao:", about: "http://www.bioassayontology.org/bao#"}); // BAO_0000134
// MERGE(:Resolver {name: "Gene Ontology", url: "http://purl.bioontology.org/ontology/GO/"}); // GO:0071735
// MERGE(:Resolver {name: "CL", url: "http://purl.bioontology.org/ontology/CL/"}); // CL:0000583
// MERGE(:Resolver {name: "Uniprot", url: "https://www.uniprot.org/uniprot/"}); // P0DTC2
// MERGE(:Resolver {name: "ChEBI", url: "http://www.ebi.ac.uk/chebi/searchId.do?chebiId="}); // CHEBI:29687
// MERGE(:Resolver {name: "Disease ontology", url: "http://purl.bioontology.org/ontology/DOID/"}); // DOID:2801
