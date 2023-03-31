"""Graph processing pipeline."""

from common.logging import configure_logging
from neotools.flow import (
    DetachDeleteAll,
    run_flow,
    SimpleDbTask,
    UpdateAttrIfNull,
    UpdateOrCreateTask,
    VerifyTask,
)
from sdg import DB


create_unique_h_entity_combo_id_constraint = SimpleDbTask(
    "Ensure that H_Entity.combo_id is unique",
    "CREATE CONSTRAINT h_entity_id IF NOT EXISTS ON (h:H_Entity) ASSERT h.combo_id IS UNIQUE",
)
create_unique_term_text_constraint = SimpleDbTask(
    "Ensure that Term.text is unique",
    "CREATE CONSTRAINT term_text_ IF NOT EXISTS ON (te:Term) ASSERT te.text IS UNIQUE",
)

delete_all_cond_tags = DetachDeleteAll("CondTag")

delete_all_terms = DetachDeleteAll("Term")

normalize_journal_name = UpdateOrCreateTask(
    "Normalize journal names",
    "MATCH (a:SDArticle) RETURN a",
    "SET a.journalName = toLower(a.journalName)",
)

normalize_tag_text = UpdateOrCreateTask(
    "trim and tolower text",
    "MATCH(t:SDTag) RETURN t",
    "SET t.norm_text = toLower(trim(t.text))",
)

set_default_sd_tag_text = UpdateOrCreateTask(
    "trim and tolower text",
    "MATCH(t:SDTag) WHERE t.text = '' RETURN t",
    "SET t.text = toLower(t.ext_names)",
)

delete_empty_tags = UpdateOrCreateTask(
    "remove sick tags with no name and no ext_names",
    "MATCH(t:SDTag)-[r]-() WHERE t.text = '' AND t.ext_names = '' RETURN r, t",
    "DELETE r, t",
)

set_default_sd_tag_ext_names = UpdateAttrIfNull("SDTag", "ext_names")
set_default_sd_tag_ext_ids = UpdateAttrIfNull("SDTag", "ext_ids")
set_default_sd_tag_ext_dbs = UpdateAttrIfNull("SDTag", "ext_dbs")
set_default_sd_tag_type = UpdateAttrIfNull("SDTag", "type")
set_default_sd_tag_role = UpdateAttrIfNull("SDTag", "role")

set_default_figure_position_idx = UpdateOrCreateTask(
    "replace NULL SDTag.role with empty string for consistency",
    "MATCH(f:Fig) WHERE NOT EXISTS(f.position_idx) RETURN f",
    "SET f.position_idx = ''",
)

set_default_panel_id = UpdateAttrIfNull("Panel", "panel_id")

delete_empty_contribs = UpdateOrCreateTask(
    "Delete Contribs with all NULL fields",
    "MATCH (au:Contrib) WHERE au.collab IS NULL AND au.surname IS NULL AND au.given_names IS NULL RETURN au",
    "DETACH DELETE au",
)
set_default_contrib_surname = UpdateAttrIfNull("Contrib", "surname")
set_default_contrib_given_names = UpdateAttrIfNull("Contrib", "given_names")
set_default_contrib_collab = UpdateAttrIfNull("Contrib", "collab")

delete_all_sd_contribs = DetachDeleteAll("SDContrib")

condense_tags_with_same_ext_id_and_role = UpdateOrCreateTask(
    "Condense tags with same ext id and role",
    """
    MATCH (p:SDPanel)-->(t:SDTag)
    WHERE t.ext_ids <> ''
    WITH DISTINCT p, t.role AS role, t.type as type, t.category as category, t.ext_ids AS ext_ids, COLLECT(DISTINCT (t.norm_text)) AS text, COUNT(DISTINCT t) AS N
    ORDER BY N DESC
    RETURN DISTINCT p, role, type, category, ext_ids, text[0] AS most_used_text
    """,
    """
    CREATE (c:CondTag {role: role, type: type, category: category, ext_ids: ext_ids, text: most_used_text})
    CREATE (p)-[rel:HasCondTag]->(c)
    """,
)
add_condensed_into_relationship_same_ext_id_and_role = UpdateOrCreateTask(
    "Add Condensed_into relationship for tags with same ext id and role",
    """
    MATCH (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
    WHERE t.role = c.role AND t.ext_ids = c.ext_ids AND t.type = c.type
    RETURN DISTINCT t, c
    """,
    "CREATE (t)-[:Condensed_into]->(c)",
)

condense_tags_with_same_text_type_role = UpdateOrCreateTask(
    "Condense tags with no ext_ids but same text, type, and role",
    """
    MATCH (p:SDPanel)-->(t:SDTag)
    WHERE t.ext_ids = '' AND (t.category <> '' OR t.type <> '')
    RETURN DISTINCT p, t.norm_text AS text, t.role AS role, t.type AS type, t.category AS category
    """,
    """
    CREATE (c:CondTag {role: role, type:type, category: category, ext_ids: '', text: text})
    CREATE (p)-[:HasCondTag]->(c)
    """,
)
add_condensed_into_relationship_same_text_type_role = UpdateOrCreateTask(
    "Add Condensed_into relationship for tags with no ext_ids but same text, type, and role",
    """
    MATCH (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
    WHERE
        c.ext_ids = ''
        AND t.ext_ids = ''
        AND t.role = c.role
        AND t.type = c.type
        AND t.category = c.category
        AND t.norm_text = c.text
    RETURN DISTINCT t, c
    """,
    "CREATE (t)-[:Condensed_into]->(c)",
)

verify_no_sd_tag_linked_to_multiple_cond_tags = VerifyTask(
    "Confirm that no SDTag is linked to multiple CondTags",
    """
    MATCH (t:SDTag)-[r:Condensed_into]->(ct:CondTag)
    WITH t, COUNT(DISTINCT ct) AS N
    WHERE N > 1
    RETURN COUNT(t)
    """,
    0,
)
verify_all_cond_tags_have_text = VerifyTask(
    "Confirm that all CondTag have a non-empty text property",
    """
    MATCH (ct:CondTag)
    WHERE ct.text = '' OR ct.text IS NULL
    RETURN COUNT(ct)
    """,
    0,
)

create_hybrid_entities_from_cond_tags_with_ext_id = UpdateOrCreateTask(
    "Create hybrid entities from CondTag with ext_id",
    """
    MATCH (ct:CondTag)
    WHERE ct.ext_ids <> ''
    RETURN DISTINCT split(ct.ext_ids,'///') as ids, ct.type AS type, ct.text AS text, ct.category AS category, ct
    """,
    """
    UNWIND ids AS id
    MERGE (hyb:H_Entity {combo_id: category + ':' + type + ':' + id})
    ON CREATE SET hyb.ext_ids = id, hyb.type = type, hyb.category = category, hyb.name = text
    MERGE (ct)-[:Identified_by]->(hyb)
    """,
)

create_hybrid_entities_from_cond_tags_without_ext_id = UpdateOrCreateTask(
    "Create hybrid entities from CondTag without ext_id",
    """
    MATCH (ct:CondTag)
    WHERE ct.ext_ids = ''
    RETURN ct.text AS text, ct.type AS type, ct.category AS category, ct
    """,
    """
    MERGE (hyb:H_Entity {combo_id: category + ':' + type + ':' + text})
    ON CREATE SET hyb.ext_ids = '', hyb.type = type, hyb.category = category, hyb.name = text 
    MERGE (ct)-[:Identified_by]->(hyb)
    """,
)

verify_no_h_entities_without_name = VerifyTask(
    "report H_Entity with no names",
    "MATCH (h:H_Entity) WHERE h.name = '' RETURN COUNT(h)",
    0,
)

create_unique_terms = UpdateOrCreateTask(
    "Create unique terms",
    """
    MATCH (t:SDTag)-[:Condensed_into]->(c:CondTag)-[:Identified_by]->(hyb:H_Entity)
    RETURN DISTINCT t.norm_text AS text, hyb
    """,
    """
    MERGE (te:Term {text: text})
    MERGE (hyb)-[r:Has_text]->(te)
    """,
)

set_term_popularities = UpdateOrCreateTask(
    "Add popularity frequency to terms",
    """
    MATCH (sd:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(ct:CondTag)-[:Identified_by]->(h:H_Entity)-[:Has_text]->(t:Term)
    RETURN t, COUNT(DISTINCT p) AS freq
    """,
    "SET t.freq_in_panel = freq",
)

add_hypotheses_at_cond_tag_level = UpdateOrCreateTask(
    "infer tested hypotheses at condensed tag level",
    """
    MATCH 
        (p:SDPanel)-[:HasCondTag]->(intervention:CondTag {role: 'intervention'}),
        (p:SDPanel)-[:HasCondTag]->(assayed:CondTag {role: 'assayed'})
    RETURN intervention, assayed
    """,
    "MERGE (intervention)-[:H]->(assayed)",
)


class SetEntityScale(UpdateOrCreateTask):
    def __init__(self, entity_type, scale):
        super().__init__(
            f"Set scale of {entity_type} entities to {scale}",
            f"MATCH (e:H_Entity) WHERE e.type = '{entity_type}' RETURN e",
            f"SET e.scale = {scale}",
        )


set_molecule_entity_scale = SetEntityScale("molecule", 1)
set_gene_entity_scale = SetEntityScale("gene", 2)
set_protein_entity_scale = SetEntityScale("protein", 2)
set_geneprod_entity_scale = SetEntityScale("geneprod", 2)
set_subcellular_entity_scale = SetEntityScale("subcellular", 3)
set_cell_entity_scale = SetEntityScale("cell", 4)
set_tissue_entity_scale = SetEntityScale("tissue", 5)
set_organism_entity_scale = SetEntityScale("organism", 6)

add_article_pub_date_and_abstract = UpdateOrCreateTask(
    "copy publication date and abstract from jats articles to SDArticles",
    """
    MATCH (jats:Article), (a:SDArticle)
    WHERE jats.doi = a.doi
    WITH DISTINCT
        jats.doi AS doi,
        jats.publication_date AS pub_date,
        jats.abstract AS abstract,
        a
    ORDER BY pub_date DESC // most recent first
    RETURN DISTINCT doi, COLLECT(pub_date)[0] AS most_recent, COLLECT(abstract)[0] AS abstr, a
    """,
    "SET a += {pub_date: most_recent, abstract: abstr}",
)

link_articles_to_contribs = UpdateOrCreateTask(
    "Link to authors via SDContrib nodes",
    """
    MATCH (jats:Article), (sd:SDArticle)
    WHERE jats.doi = sd.doi
    WITH DISTINCT sd.doi AS doi, sd, jats
    ORDER BY jats.publication_date DESC
    WITH DISTINCT doi, sd, COLLECT(jats)[0] AS most_recent
    MATCH (most_recent)-[:has_author]->(au:Contrib)
    RETURN DISTINCT doi, sd, au
    """,
    """
    MERGE (sd)-[r:has_author]->(sdau:SDContrib {
        position_idx: au.position_idx,
        source: au.source,
        given_names: au.given_names,
        surname: au.surname,
        concat_name: au.given_names + ' ' + au.surname + ' ' + au.collab
    })
    """,
)


Tasks = [
    create_unique_h_entity_combo_id_constraint,
    create_unique_term_text_constraint,
    delete_all_cond_tags,
    delete_all_terms,
    normalize_journal_name,
    normalize_tag_text,
    set_default_sd_tag_text,
    delete_empty_tags,
    set_default_sd_tag_ext_names,
    set_default_sd_tag_ext_ids,
    set_default_sd_tag_ext_dbs,
    set_default_sd_tag_type,
    set_default_sd_tag_role,
    set_default_figure_position_idx,
    set_default_panel_id,
    delete_empty_contribs,
    set_default_contrib_surname,
    set_default_contrib_given_names,
    set_default_contrib_collab,
    delete_all_sd_contribs,
    condense_tags_with_same_ext_id_and_role,
    add_condensed_into_relationship_same_ext_id_and_role,
    condense_tags_with_same_text_type_role,
    add_condensed_into_relationship_same_text_type_role,
    verify_no_sd_tag_linked_to_multiple_cond_tags,
    verify_all_cond_tags_have_text,
    create_hybrid_entities_from_cond_tags_with_ext_id,
    create_hybrid_entities_from_cond_tags_without_ext_id,
    verify_no_h_entities_without_name,
    create_unique_terms,
    set_term_popularities,
    add_hypotheses_at_cond_tag_level,
    set_molecule_entity_scale,
    set_gene_entity_scale,
    set_protein_entity_scale,
    set_geneprod_entity_scale,
    set_subcellular_entity_scale,
    set_cell_entity_scale,
    set_tissue_entity_scale,
    set_organism_entity_scale,
    add_article_pub_date_and_abstract,
    link_articles_to_contribs,
]


if __name__ == "__main__":
    configure_logging()
    run_flow(DB, Tasks, "processing the graph")
