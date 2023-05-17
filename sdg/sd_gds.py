"""Graph data science pipeline."""

from common.logging import configure_logging
from neotools.flow import run_flow, SimpleDbTask, UpdateOrCreateTask
from sdg import DB

class TryDropProjection(SimpleDbTask):
    def __init__(self, projection_name):
        super().__init__(
            f"Try to drop projection {projection_name}",
            f"CALL gds.graph.drop('{projection_name}', false) YIELD graphName",
        )


assay_quasi_synonyms_task = UpdateOrCreateTask(
    "H_Entity - Term - H_Entity network for quasi-synonyms",
    """
    MATCH (entity_1:H_Entity)-[:Has_text]->(bridge:Term)<-[:Has_text]-(entity_2:H_Entity)
    WHERE
        entity_1 <> entity_2 AND
        entity_1.category = 'assay' AND entity_2.category = 'assay'
        // TODO: and usage of this term compared to all terms for this entity is > 10% 
    RETURN entity_1, entity_2
    """,
    "MERGE (entity_1)-[r:related_concept]-(entity_2)",
)

reset_assay_conecpt_id_task = UpdateOrCreateTask(
    "Reset assay concept id of all H_Entities",
    "MATCH (h:H_Entity) RETURN h",
    "SET h.assay_concept_id = Null",
)

gds_drop_projection_for_assay_quasi_synonyms_task = TryDropProjection("assay-quasi-synonyms")
gds_projection_for_assay_quasi_synonyms_task = SimpleDbTask(
    "Create the necessary GDS projection for community detection of assay quasi-synonyms",
    """
    CALL gds.graph.project.cypher(
        // projection name
        'assay-quasi-synonyms',
        // nodeQuery
        'MATCH (h:H_Entity {category: "assay"}) RETURN id(h) AS id',
        // relationshipQuery
        'MATCH (h1:H_Entity {category: "assay"})-[:related_concept]-(h2:H_Entity {category: "assay"}) RETURN id(h1) AS source, id(h2) AS target'
    )
    """,
)
community_detection_for_assay_quasi_synonyms_task = SimpleDbTask(
    "Community detection for assay quasi-synonyms",
    """
    CALL gds.louvain.write(
        'assay-quasi-synonyms',
        {
            writeProperty: 'assay_concept_id',
            logProgress: False
        }
    )
    """,
)

reset_assay_concept_name_and_ext_ids_task = UpdateOrCreateTask(
    "Reset assay concept name and ext_ids of all H_Entities",
    "MATCH (entity:H_Entity) WHERE EXISTS(entity.assay_concept_name) RETURN entity",
    "SET entity.assay_concept_name = NULL, entity.assay_concept_ext_ids = NULL",
)

named_clusters_of_assay_related_concepts_task = UpdateOrCreateTask(
    "adding cluster name based on the most generic entity",
    """
    MATCH (entity:H_Entity {category: 'assay'})-[:Has_text]->(te:Term)
    // popularity could be measure as SUM(te.freq_in_panels) or simpler as here as number of linked terms as an indication of how generic an entity name is
    WITH
        entity,
        COUNT(DISTINCT te) AS entity_generality
    ORDER BY entity_generality DESC
    RETURN
        entity.assay_concept_id AS concept_id,
        COUNT(DISTINCT entity) AS size,
        // the first entity will be the entity that is linked to the most quasi synonymous terms
        COLLECT(entity)[0] AS most_popular_entity, 
        COLLECT(DISTINCT entity) AS cluster
    """,
    """
    UNWIND cluster AS entity
    SET
        entity.assay_concept_name = most_popular_entity.name,
        entity.assay_concept_ext_ids = most_popular_entity.ext_ids
    """,
)

geneprod_quasi_synonyms_task = UpdateOrCreateTask(
    "H_Entity - Term - H_Entity network for quasi-synonyms",
    """
    MATCH (entity_1:H_Entity)-[:Has_text]->(bridge:Term)<-[:Has_text]-(entity_2:H_Entity)
    WHERE
        id(entity_1) > id(entity_2) AND
        entity_1.type IN ['gene', 'protein', 'geneprod'] AND 
        entity_2.type IN ['gene', 'protein', 'geneprod']
        // TODO: and usage of this term compared to all terms for this entity is > 10%
    RETURN entity_1, entity_2
    """,
    "MERGE (entity_1)-[r:related_geneprod]-(entity_2)",
)

reset_geneprod_concept_id_task = UpdateOrCreateTask(
    "Reset geneprod concept id of all H_Entities",
    "MATCH (h:H_Entity) RETURN h",
    "SET h.geneprod_concept_id = Null",
)

gds_drop_projection_for_geneprod_quasi_synonyms_task = TryDropProjection("geneprod-quasi-synonyms")
gds_projection_for_geneprod_quasi_synonyms_task = SimpleDbTask(
    "Create the necessary GDS projection for community detection of assay quasi-synonyms",
    """
    CALL gds.graph.drop('geneprod-quasi-synonyms', false) YIELD graphName;  // drop projection if it exists
    CALL gds.graph.project.cypher(
        // projection name
        'geneprod-quasi-synonyms',
        // nodeQuery
        'MATCH (h:H_Entity)
        WHERE h.type IN ["gene", "protein", "geneprod"]
        RETURN id(h) AS id',
        // relationshipQuery
        'MATCH (h1:H_Entity)-[:related_geneprod]-(h2:H_Entity)
        WHERE
        h1.type IN ["gene", "protein", "geneprod"] AND 
        h2.type IN ["gene", "protein", "geneprod"]
        RETURN id(h1) AS source, id(h2) AS target'
    )
    """,
)
community_detection_for_geneprod_quasi_synonyms_task = SimpleDbTask(
    "geneprod communities",
    """
    CALL gds.louvain.stream(
        'geneprod-quasi-synonyms',
        {
            includeIntermediateCommunities: True,
            logProgress: False
        }
    )
    YIELD nodeId, communityId, intermediateCommunityIds
    WITH gds.util.asNode(nodeId) AS node, intermediateCommunityIds[0] AS subcommunityId
    SET node.geneprod_concept_id = subcommunityId
    """,
)

reset_geneprod_concept_id_name_task = UpdateOrCreateTask(
    "Reset geneprod concept id of all H_Entities",
    "MATCH (h:H_Entity) RETURN h",
    "SET h.geneprod_concept_name = Null",
)

set_geneprod_concept_name_task = UpdateOrCreateTask(
    "named clusters of geneprod related concepts",
    """
    MATCH (entity:H_Entity)-[:Has_text]->(term:Term)
    WHERE entity.type IN ['gene' , 'protein', 'geneprod']
    WITH entity, term
    ORDER BY term.freq_in_panel DESC
    RETURN
        entity.geneprod_concept_id AS concept_id, 
        COLLECT(term)[0] AS most_popular_term, 
        COLLECT(DISTINCT entity) AS cluster
    """,
    """
    UNWIND cluster AS entity
    SET entity.geneprod_concept_name = most_popular_term.text
    """,
)


create_hypotheses_summaries_at_paper_level_task = UpdateOrCreateTask(
    "Create hypotheses summaries at paper level",
    """
    MATCH
        (art:SDArticle)-->(f1:SDFigure)-->(p1:SDPanel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
        (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
    RETURN art, ih, ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
    """,
    """
    MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
    MERGE (art)-[:HasH {n_panels: N_p, n_figures: N_f}]->(h)
    """,
)

add_text_descr_to_hypothesis_task = UpdateOrCreateTask(
    "Add text description to hypothesis",
    "MATCH (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity) RETURN h, ih, ah",
    "SET h.description = ih.name + ' --> ' + ah.name",
)

reset_self_test_hypotheses_task = UpdateOrCreateTask(
    "Flag possible self-test hypotheses",
    "MATCH (h:Hypothesis) RETURN h",
    "SET h.self_test = False",
)

flag_self_test_hypotheses_task = UpdateOrCreateTask(
    "Flag possible self-test hypotheses",
    """
    MATCH
        (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity),
        (ih)-->(same:Term)
    WITH h, ah, same
    MATCH (ah)-->(same)
    RETURN h
    """,
    "SET h.self_test = True",
)

reset_boring_hypotheses_task = UpdateOrCreateTask(
    "reset boring hypotheses",
    "MATCH (h:Hypothesis) RETURN h",
    "SET h.boring = False",
)

flag_boring_hypotheses_task = UpdateOrCreateTask(
    "Flag possible boring entities, helpful to filter them later. Exclusion list based on SourceData normalized and reporter entities",
    """
    MATCH (:SDCollection {name: 'PUBLICSEARCH'})-->(:SDArticle)-->(:SDFigure)-->(:SDPanel)-->(ct:CondTag)-->(h:H_Entity)-->(te:Term)
    RETURN DISTINCT h.name AS name, COLLECT(DISTINCT te.text) AS synonyms, COLLECT(DISTINCT ct) AS cts, 1.0*COUNT(DISTINCT ct) AS N
    """,
    """
    UNWIND cts as ct
    WITH DISTINCT name, synonyms, N, ct.role as role, 1.0*COUNT(DISTINCT ct) AS N_role
    WITH name, synonyms, role, N, N_role, 100.0*(N_role / N) AS fract
    ORDER BY N DESC, fract DESC
    WITH name, synonyms, N, COLLECT(role)[0] AS dominant_role, COLLECT(fract)[0] AS dom_fract
    WHERE 
    ((dominant_role = 'reporter') AND dom_fract > 75)
    OR
    ((dominant_role = 'normalizing') AND dom_fract > 80 AND N > 20)
    OR
    ((dominant_role = 'component') AND dom_fract > 75 AND N > 100)
    WITH COLLECT(name) AS all
    UNWIND apoc.coll.toSet(all) as excluded_term
    MATCH (h:H_Entity)-->(te:Term {text: excluded_term})
    SET h.boring = True
    """,
)

add_weights_to_hypotheses_nodes_task = UpdateOrCreateTask(
    "Add weights to hypotheses nodes",
    """
    MATCH (a:SDArticle)-[h:HasH]->(hyp:Hypothesis)
    RETURN
        hyp,
        SUM(DISTINCT h.n_panels) AS sum_n_panels,
        SUM(DISTINCT h.n_figures) AS sum_n_figures,
        COUNT(DISTINCT a) AS n_articles
    """,
    """
    SET 
        hyp.n_panels = sum_n_panels,
        hyp.n_figures = sum_n_figures,
        hyp.n_articles = n_articles
    """,
)

tasks = [
    assay_quasi_synonyms_task,
    reset_assay_conecpt_id_task,
    gds_drop_projection_for_assay_quasi_synonyms_task,
    gds_projection_for_assay_quasi_synonyms_task,
    community_detection_for_assay_quasi_synonyms_task,
    reset_assay_concept_name_and_ext_ids_task,
    named_clusters_of_assay_related_concepts_task,
    geneprod_quasi_synonyms_task,
    reset_geneprod_concept_id_task,
    gds_drop_projection_for_geneprod_quasi_synonyms_task,
    gds_projection_for_geneprod_quasi_synonyms_task,
    community_detection_for_geneprod_quasi_synonyms_task,
    reset_geneprod_concept_id_name_task,
    set_geneprod_concept_name_task,
    create_hypotheses_summaries_at_paper_level_task,
    add_text_descr_to_hypothesis_task,
    reset_self_test_hypotheses_task,
    flag_self_test_hypotheses_task,
    reset_boring_hypotheses_task,
    flag_boring_hypotheses_task,
    add_weights_to_hypotheses_nodes_task,
]



if __name__ == "__main__":
    configure_logging()
    run_flow(DB, tasks, "doing graph data science")
