
// ASSAY QUASI SYNONYMS
// H_Entity - Term - H_Entity network for quasi-synonyms
MATCH
  (entity_1:H_Entity)-[:Has_text]->(bridge:Term)<-[:Has_text]-(entity_2:H_Entity)
WHERE
  entity_1 <> entity_2 AND
  entity_1.category = "assay" AND entity_2.category = "assay"
  // TODO: and usage of this term compared to all terms for this entity is > 10% 
MERGE
  (entity_1)-[r:related_concept]-(entity_2)
RETURN
  COUNT(DISTINCT r) AS `assay quasi synonyms relationships;


// COMMUNITY DETECTION FOR ASSAY QUASI SYNONYMS
MATCH (h:H_Entity) SET h.assay_concept_id = Null;
CALL gds.louvain.write(
  {
    nodeQuery: 'MATCH (h:H_Entity {category: "assay"}) RETURN id(h) AS id',
    relationshipQuery: 'MATCH (h1:H_Entity {category: "assay"})-[:related_concept]-(h2:H_Entity {category: "assay"}) RETURN id(h1) AS source, id(h2) AS target',
    writeProperty: 'assay_concept_id',
    concurrency: 4
  }
);


// adding cluster name based on the most generic entity
MATCH (entity:H_Entity) WHERE EXISTS(entity.concept_name) SET entity.concept_name = NULL, entity.concept_ext_ids=NULL;
MATCH (entity:H_Entity {category: "assay"})-[:Has_text]->(te:Term)
// popularity could be measure as SUM(te.freq_in_panels) or simpler as here as number of linked terms as an indication of how generic an entity name is
WITH entity, COUNT(DISTINCT te) AS entity_generality
ORDER BY entity_generality DESC
WITH
  entity.assay_concept_id AS concept_id, 
  COUNT(DISTINCT entity) AS size,
  // the first entity will be the entity that is linked to the most quasi synonymous terms
  COLLECT(entity)[0] AS most_popular_entity, 
  COLLECT(DISTINCT entity) AS cluster
UNWIND cluster AS entity
SET entity.concept_name = most_popular_entity.name, entity.concept_ext_ids = most_popular_entity.ext_ids
RETURN DISTINCT 
  COUNT(DISTINCT entity.assay_concept_id) AS `named clusters of assay related concepts`;


// GENEPROD QUASI SYNONYMS
// H_Entity - Term - H_Entity network for quasi-synonyms
MATCH
  (entity_1:H_Entity)-[:Has_text]->(bridge:Term)<-[:Has_text]-(entity_2:H_Entity)
WHERE
  id(entity_1) > id(entity_2) AND
  (entity_1.type = "gene" OR entity_1.type='protein' OR entity_1.type='geneprod') AND 
  (entity_2.type = "gene" OR entity_2.type='protein' OR entity_2.type='geneprod')
  // TODO: and usage of this term compared to all terms for this entity is > 10%
MERGE
  (entity_1)-[r:related_geneprod]-(entity_2)
RETURN
  COUNT(DISTINCT r) AS `geneprod quasi synonyms relationships;


// COMMUNITY DETECTION FOR GENEPROD QUASI SYNONYMS
MATCH (h:H_Entity) SET h.geneprod_concept_id = Null;
CALL gds.louvain.stream(
  {
    nodeQuery: 
      'MATCH (h:H_Entity)
       WHERE (h.type = "gene" OR h.type="protein" OR h.type="geneprod")
       RETURN id(h) AS id',
    relationshipQuery: 
    'MATCH (h1:H_Entity)-[:related_geneprod]-(h2:H_Entity)
    WHERE
      (h1.type = "gene" OR h1.type="protein" OR h1.type="geneprod") AND 
      (h2.type = "gene" OR h2.type="protein" OR h2.type="geneprod")
    RETURN id(h1) AS source, id(h2) AS target',
    includeIntermediateCommunities: True
  }
) YIELD nodeId, communityId, intermediateCommunityIds
WITH gds.util.asNode(nodeId) AS node, intermediateCommunityIds[0] AS subcommunityId
SET node.louvain_community_id = subcommunityId
// //for testing
// RETURN COLLECT(DISTINCT node.name) AS subcommunity, subcommunityId, COUNT(node) AS N
// ORDER BY N DESC
// LIMIT 100
RETURN COUNT(DISTINCT subcommunityId) AS `geneprod communities`
;


// adding concept geneprod name
MATCH (entity:H_Entity) SET entity.geneprod_concept_name = NULL;
MATCH (entity:H_Entity)-[:Has_text]->(term:Term)
WHERE (entity.type = "gene" OR entity.type='protein' OR entity.type='geneprod')
WITH entity, term
ORDER BY term.freq_in_panel  DESC
WITH
  entity.geneprod_concept_id AS concept_id, 
  COLLECT(term)[0] AS most_popular_term, 
  COLLECT(DISTINCT entity) AS cluster
UNWIND cluster AS entity
SET entity.geneprod_concept_name = most_popular_term.text //, entity.geneprod_concept_ext_ids = 
RETURN DISTINCT 
  COUNT(DISTINCT entity.geneprod_concept_name) AS `named clusters of geneprod related concepts`;


//create hypotheses summaries at paper level
MATCH 
  (art:SDArticle)-->(f1:SDFigure)-->(p1:SDPanel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
  (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
// RETURN art,ih,ah,COLLECT(f1),COLLECT(p1),COLLECT(i1),COLLECT(a1),COUNT(DISTINCT p1) AS N_p,COUNT(DISTINCT f1) AS N_f ORDER BY N_p DESC LIMIT 1
WITH art,ih,ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
  MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
  MERGE (art)-[:HasH {n_panels:N_p, n_figures:N_f}]->(h)
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
MATCH (:SDCollection {name: "PUBLICSEARCH"})-->(:SDArticle)-->(:SDFigure)-->(:SDPanel)-->(ct:CondTag)-->(h:H_Entity)-->(te:Term)
WITH DISTINCT h.name AS name, COLLECT(DISTINCT te.text) AS synonyms, COLLECT(DISTINCT ct) AS cts, 1.0*COUNT(DISTINCT ct) AS N
UNWIND cts as ct
WITH DISTINCT name, synonyms, N, ct.role as role, 1.0*COUNT(DISTINCT ct) AS N_role
WITH name, synonyms, role, N, N_role, 100.0*(N_role / N) AS fract
ORDER BY N DESC, fract DESC
WITH name, synonyms, N, COLLECT(role)[0] AS dominant_role, COLLECT(fract)[0] AS dom_fract
WHERE 
  ((dominant_role = "reporter") AND dom_fract > 75)
  OR
  ((dominant_role = "normalizing") AND dom_fract > 80 AND N > 20)
  OR
  ((dominant_role = "component") AND dom_fract > 75 AND N > 100)
WITH COLLECT(name) AS all
UNWIND apoc.coll.toSet(all) as excluded_term
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
WHERE
  (NOT up.boring) AND (NOT ah.boring) AND (NOT do.boring) AND
  h1.n_panels > 2 AND h2.n_panels > 2
MERGE (h1)-[chain:hyp_chain]->(h2)
RETURN COUNT(DISTINCT chain) AS `hypothesis chains`;


// concept-as-node network
MATCH (co:Concept {type: "geneproduct"}) DETACH DELETE co;
MATCH
  (up:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(do:H_Entity)
WHERE
  (NOT up.boring) AND 
  (NOT do.boring) AND
  h.n_panels > 2 AND
  EXISTS(up.geneprod_concept_id) AND 
  EXISTS(up.geneprod_concept_id) AND
  up.geneprod_concept_id <> do.geneprod_concept_id
WITH DISTINCT
  up.geneprod_concept_id AS up_concept_id,
  up.geneprod_concept_name AS up_concept_name,
  do.geneprod_concept_id AS do_concept_id,
  do.geneprod_concept_name AS do_concept_name,
  SUM(h.n_panels) AS sum_n_panels,
  COLLECT(DISTINCT h) AS hypotheses
MERGE (co_up:Concept {type: "geneproduct", concept_id: up_concept_id, concept_name: up_concept_name})
MERGE (co_do:Concept {type: "geneproduct", concept_id: do_concept_id, concept_name: do_concept_name})
MERGE (co_up)-[r:concept_test {sum_n_panels: sum_n_panels}]->(co_do)
WITH DISTINCT co_up, co_do, hypotheses, r
UNWIND hypotheses AS h
MERGE (co_up)-[:intervention_concept]->(h)-[:assay_concept]->(co_do)
RETURN COUNT(DISTINCT r) AS `concept-to-concept relationships`;


// for each paper, rank dominant hypotheses
// MATCH (a:SDArticle)-[r:HasH]->(h:Hypothesis)
// WITH a, r, h
// ORDER BY r.n_panels DESC
// WITH a, COLLECT(r) AS ranked
// UNWIND range(0, size(ranked)-1) as i
// WITh a, ranked[i] AS r, i
// SET r.rank = i+1;


// CALL gds.louvain.stream(
// {
// nodeQuery:
// "MATCH 
//     (coll:SDCollection)-->(a:SDArticle)-->(h:Hypothesis)--(entity:H_Entity)
// WHERE
//     entity.type IN ['gene', 'protein', 'geneprod'] AND
//     // coll.name = 'PUBLICSEARCH' AND
//     a.journalName = 'biorxiv'
//     // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
//     // DATETIME(a.pub_date) < DATETIME($date)
//     AND (h.n_articles >= 2 OR h.n_panels >= 2 * 2)
//     AND (NOT h.self_test)
//     AND (NOT entity.boring)
//     AND (NOT entity.name IN split('.,-()abcdefg1234567890', ''))
// RETURN DISTINCT 
//     id(entity) AS id"
// ,    
// relationshipQuery:
// "MATCH 
//     (coll:SDCollection)-->(a:SDArticle)-->(h:Hypothesis),
//     (source:H_Entity)-->(h:Hypothesis)-->(target:H_Entity)
// WHERE
//     source.type IN ['gene', 'protein', 'geneprod'] AND target.type IN ['gene', 'protein', 'geneprod'] AND
//     // coll.name = 'PUBLICSEARCH' AND
//     a.journalName = 'biorxiv'
//     // coll.name IN ['Cell Biology', 'Molecular Biology', 'Biochemistry', 'Cancer Biology', 'Developmental Biology', 'Microbiology'] AND
//     // DATETIME(a.pub_date) < DATETIME($date)
//     AND (h.n_articles >= 2 OR h.n_panels >= 2 * 2)
//     AND (NOT h.self_test)
//     AND (NOT source.boring) AND (NOT target.boring)
//     AND (NOT source.name IN split('.,-()abcdefg1234567890', ''))
//     AND (NOT target.name IN split('.,-()abcdefg1234567890', '')) //AND
//     // id(source) > id(target)  // if undirected, avoid permutation
// RETURN DISTINCT 
//     id(source) AS source, id(target) AS target",
//     includeIntermediateCommunities: True
// }
// ) YIELD nodeId, communityId, intermediateCommunityIds
// WITH gds.util.asNode(nodeId) AS node, communityId, intermediateCommunityIds
// // SET node.louvain_community_id = communityId, node.louvain_subcommunityId = intermediateCommunity[0]
// WITH COLLECT(node.name) AS subcommunity, communityId, intermediateCommunityIds[0] AS subcommunityId, COUNT(node) AS N_sub
// ORDER BY N_sub DESC
// RETURN COLLECT(subcommunity) AS community, communityId, COLLECT(subcommunityId) AS communityIds, SUM(N_sub) AS N
// ORDER BY N DESC
// LIMIT 100 

// intercommunity bridges
// MATCH (up:H_Entity)-->(h:Hypothesis)-->(do:H_Entity)
// WHERE
//   up.louvain_geneprod_community <> do.louvain_geneprod_community AND 
//   NOT up.boring AND NOT do.boring
// WITH up, do, h
// MATCH (h)<-[r:HasH {rank:1}]-(a:SDArticle)
// WITH up, do, h, COLLECT(DISTINCT [a.title, a.doi]) AS titles
// RETURN up.name, do.name, h.n_panels AS N, COLLECT(DISTINCT [a.title, a.doi]) AS titles
// ORDER BY N DESC
// LIMIT 100

// CALL gds.betweenness.stream({
//   nodeQuery:
//     'MATCH (entity:H_Entity)
//      WHERE 
//        EXISTS(entity.louvain_geneprod_community)
//      RETURN id(entity) AS id',
//   relationshipQuery:
//      'MATCH
//        (source:H_Entity)-->(h:Hypothesis)-->(target:H_Entity)
//       WHERE
//        source.louvain_geneprod_community = target.louvain_geneprod_community
//       RETURN
//        id(source) AS source, id(target) AS target'
// })
// YIELD nodeId, score
// WITH gds.util.asNode(nodeId) AS n, score
// ORDER BY score DESC
// RETURN COLLECT(DISTINCT n.name) AS names, n.louvain_geneprod_community, COUNT(n) AS N
// ORDER BY N DESC
// LIMIT 20


// // entity embedding based on related_concept network
// MATCH (h:H_Entity) WHERE EXISTS(h.assay_concept_embedding) SET h.assay_concept_embedding = NULL;
// CALL gds.fastRP.write(
//   {
//     nodeQuery: 'MATCH (h:H_Entity {category: "assay"}) RETURN id(h) AS id',
//     relationshipQuery: 'MATCH (h1:H_Entity {category: "assay"})-[:related_concept]-(h2:H_Entity {category: "assay"}) RETURN id(h1) AS source, id(h2) AS target',
//     embeddingDimension: 1024,
//     iterationWeights: [1.0, 1.0],
//     writeProperty: 'assay_concept_embedding'
//   }
// );

// // derivative pseudo synonyme network based on embedding kNN
// MATCH (h:H_Entity)
// WHERE EXISTS(h.assay_concept_embedding)
// WITH {item: id(h), weights: h.assay_concept_embedding} AS selected_h
// WITH collect(selected_h) AS data
// CALL gds.alpha.ml.ann.stream({
//    data: data,
//    algorithm: 'cosine'
//  })
// YIELD item1, item2, similarity, count1, count2
// WITH gds.util.asNode(item1) AS n1, gds.util.asNode(item2) AS n2, similarity, count1, count2
// ORDER BY similarity DESC
// // RETURN n1.name, n2.name, similarity, count1, count2
// // LIMIT 100
// MERGE (n1)-[p:assay_embedding_similarity {similarity: similarity}]-(n2);

// // // community detection in derivative embedding siilarity network
// CALL gds.louvain.stream(
//   {
//     nodeQuery: 'MATCH (h:H_Entity {category: "assay"}) WHERE EXISTS(h.assay_concept_embedding) RETURN id(h) AS id',
//     relationshipQuery: 'MATCH (h1:H_Entity {category: "assay"})-[r:assay_embedding_similarity]-(h2:H_Entity {category: "assay"}) WHERE r.similarity > 0.6 RETURN id(h1) AS source, id(h2) AS target'
//   }
// )
// YIELD nodeId, communityId
// WITH COLLECT(gds.util.asNode(nodeId)) AS cluster, COUNT(gds.util.asNode(nodeId)) AS N, communityId
// RETURN cluster, N, communityId
// ORDER BY N DESC
// SKIP 0 
// LIMIT 1


// // hypotheses communities
// //reset
// MATCH (h:Hypothesis) SET h.tested_community = NULL;
// // 
// CALL gds.louvain.write({
//   nodeQuery: 'MATCH (h:Hypothesis) WHERE h.n_panels > 2 RETURN id(h) AS id',
//   relationshipQuery: 'MATCH (h1:Hypothesis)-[p:hyp_chain]->(h2:Hypothesis) WHERE h1.n_panels > 2 AND h2.n_panels > 2 RETURN id(h1) AS source, id(h2) AS target',
//   writeProperty: 'tested_community'
// });


// // PRIORITIZE BRIDGING HYPOTHESES
// MATCH (h:Hypothesis) SET h.is_hot = FALSE;
// CALL gds.betweenness.stream({
//   nodeQuery:
//     'MATCH (h:Hypothesis)
//      WHERE 
//        EXISTS(h.tested_community) AND (NOT h.self_test)
//      RETURN id(h) AS id',
//   relationshipQuery:
//      'MATCH
//        (h1:Hypothesis)-[p:hyp_chain]->(h2:Hypothesis)
//       WHERE
//         (NOT h1.self_test) AND (NOT h2.self_test) AND h1 <> h2 AND h1.tested_community=h2.tested_community
//       RETURN id(h1) AS source, id(h2) AS target'
// })
// YIELD nodeId, score
// WITH gds.util.asNode(nodeId) AS n, score
// ORDER BY score DESC
// WITH n, score, n.tested_community AS communityId
// WITH COLLECT(DISTINCT {node: n, score: score}) AS cluster, MAX(score) AS max_score, COUNT(n) AS N, percentileCont(score, 0.9) as threshold, communityId
// WHERE N > 50
// WITH [x IN cluster WHERE x.score > threshold | {node: x.node, score: 2* x.score / ((N-1)*(N-2))}] as normalized_thresholded, communityId, N
// UNWIND normalized_thresholded AS scored_node
// WITH DISTINCT scored_node.node AS node, scored_node.node.description AS description, scored_node.score as score, N, communityId
// WHERE score > 0.01
// SET node.is_hot = True
// RETURN description, score, N, communityId;





// CALL gds.fastRP.stream(
//   {
//     nodeQuery: 
//       'MATCH (h:H_Entity) RETURN id(h) AS id',
//     relationshipQuery: 
//       'MATCH (h1:H_Entity {category: "assay"})-[:related_concept]-(h2:H_Entity) RETURN id(h1) AS source, id(h2) AS target',
//     embeddiembeddingDimensionngSize: 64,
//     writeProperty: 'frp_embedding'
//   }
// );



// figure co-occurence network
// MATCH
//   (a:SDArticle)-[:has_fig]->(f:SDFigure),
//   (f)-->(:SDPanel)-->(:CondTag)-->(e1:H_Entity),
//   (f)-->(:SDPanel)-->(:CondTag)-->(e2:H_Entity)  // WARNING DOES THIS IMPLU e1 <> e2?
// WHERE
//    e1 <> e2 AND 
//    (NOT e1.boring) AND 
//    (NOT e2.boring) AND
//    id(e1) > id(e2)  // only one permuation needed since graph is undirected
// WITH 
//   e1, e2, a, COUNT(DISTINCT f) AS n_figures
// WITH 
//   e1, e2, a, n_figures
// WHERE 
//   n_figures >=2  // basic cutoff
// MERGE 
//   (e1)-[:in_fig_co]-(co:FigureCoOcurrence)-[:in_fig_co]-(e2)  // undirected
// MERGE 
//   (a)-[:HasCo {n_figures: n_figures}]->(co)
// RETURN 
//   COUNT(DISTINCT co) AS `figure co-occurences`;

// // add n_articles to HasCo relationships to aid filtering
// MATCH (a:SDArticle)-[:HasCo]->(co:FigureCoOcurrence)
// WITH co, COUNT(DISTINCT a) AS n_articles
// SET co.n_articles = n_articles
// RETURN COUNT(DISTINCT co) AS `set n_articles attribute`;


// hypothesis-as-edge network
// MATCH
//   (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity)
// WHERE (NOT ih.boring) AND (NOT ah.boring)
// MERGE (ih)-[tested:Tested]->(ah)
// RETURN COUNT(DISTINCT tested) AS `hypotheses at entity level`;


// //transfer hypothesis weight to :Tested links
// MATCH (i:H_Entity)-->(h:Hypothesis)-->(a:H_Entity), (i)-[r:Tested]->(a)
// SET
//   r.n_panels = h.n_panels,
//   r.n_figures = h.n_figures,
//   r.n_articles = h.n_articles
// RETURN DISTINCT "transferred hypothesis weight to :Tested links";


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
