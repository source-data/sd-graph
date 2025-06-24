"""Graph processing pipeline."""

from common.logging import configure_logging
from neotools.flow import (
    DetachDeleteAll,
    run_flow,
    SimpleDbTask,
    UpdateOrCreateTask,
)
from sdg import DB

purge_viz_graph_tasks = [
    DetachDeleteAll("VizCollection"),
    DetachDeleteAll("VizSubCollection"),
    DetachDeleteAll("VizPaper"),
    DetachDeleteAll("VizInfo"),
    DetachDeleteAll("VizEntity"),
    DetachDeleteAll("VizReviewDate"),
    DetachDeleteAll("VizPaperRank"),
    DetachDeleteAll("VizDescriptor"),
]

create_sd_articles = UpdateOrCreateTask(
    "creating SDArticle nodes from Article nodes",
    """
    MATCH (a:Article)
    WHERE NOT EXISTS {
        MATCH (s:SDArticle {doi: a.doi})
    }
    RETURN DISTINCT a
    """,
    """
    CREATE (sda:SDArticle {
        abstract: a.abstract,
        doi: a.doi,
        journalName: a.journal_title,
        nb_figures: 0,
        pub_date: a.publication_date,
        source: 'sd_precompute',
        title: a.title
    })
    """,
)

create_viz_papers = UpdateOrCreateTask(
    "creating VizPapers from biorxiv/medrxiv preprints",
    "MATCH (a:SDArticle) WHERE a.journalName IN ['biorxiv', 'medrxiv'] RETURN a",
    """
    MERGE (preprint:VizPaper {
        doi: a.doi,
        pub_date: toString(DATETIME(a.pub_date)),
        slug: LEFT(apoc.text.slug(a.title), 256)
    })
    """,
)

create_by_rev_service_collections = UpdateOrCreateTask(
    "creating VizCollections for the reviewing service collections",
    """
    UNWIND [
        {name: 'review commons', rank: 0},
        {name: 'peerage of science', rank: 1}, 
        {name: 'embo press', rank: 2},
        {name: 'elife', rank:3},
        {name: 'Peer Community In', rank: 4},
        {name: 'MIT Press - Journals', rank: 5},
        {name: 'peer ref', rank: 6}
    ] AS reviewing
    MATCH (rev_service:ReviewingService {name: reviewing.name})-->(val:PRDVal)<--(field:PRDField)
    WITH
        reviewing,
        rev_service,
        COLLECT(val.value) AS values,
        COLLECT(field.key) AS keys
    WITH
        reviewing, 
        rev_service,
        apoc.map.fromLists(keys, values) AS descriptor
    WITH
        reviewing,
        rev_service,
        //merging the peer review descriptor fields with attributes from the review service node
        descriptor{
            .*,
            name: rev_service.name,
            url: rev_service.url,
            peer_review_policy: rev_service.peer_review_policy
        }
    MATCH (a:Article)
    OPTIONAL MATCH (a)-[r:HasReview]->(review:Review)
    WHERE review.reviewed_by STARTS WITH reviewing.name
    OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial)
    WHERE annot.reviewed_by STARTS WITH reviewing.name
    WITH DISTINCT
        reviewing,
        descriptor,
        a.doi AS doi,
        review,
        annot
    WHERE EXISTS(review.reviewed_by) OR EXISTS(annot.reviewed_by)
    WITH DISTINCT
        reviewing,
        descriptor,
        doi,
        COLLECT(DISTINCT DATETIME(review.posting_date)) + COLLECT(DISTINCT DATETIME(annot.posting_date)) AS peer_review_dates
    UNWIND peer_review_dates AS peer_review_date
    // remove duplicate and sort to hvae most recent peer review date first
    WITH DISTINCT
        reviewing,
        descriptor,
        doi,
        peer_review_date
    ORDER BY peer_review_date DESC
    // keep most recent peer review date
    RETURN DISTINCT
        reviewing,
        descriptor,
        doi,
        COLLECT(DISTINCT peer_review_date)[0] AS earliest_review_date
    """,
    """
    WITH reviewing, descriptor, doi, earliest_review_date
    MATCH (paper:VizPaper {doi: doi})
    WITH
        reviewing,
        descriptor,
        doi,
        paper,
        paper.pub_date AS pub_date,
        earliest_review_date
    ORDER BY reviewing.rank ASC, pub_date DESC
    MERGE (col:VizCollection {name: 'refereed-preprints'})
    MERGE (subcol:VizSubCollection {name: reviewing.name})
    MERGE (subcol)-[:HasDesciption]->(descr:VizDescriptor)
    SET descr = descriptor
    MERGE (revdate:VizReviewDate {date: toString(earliest_review_date)})
    MERGE (paper)-[:HasReviewDate]->(revdate)
    MERGE (col)-[:HasSubCol]->(subcol)
    MERGE (subcol)-[:HasPaper]->(paper)
    RETURN COUNT(DISTINCT paper) AS `papers in the by reviewing service`
    """,
)

link_exp_assays = UpdateOrCreateTask(
    "linking assays for visualization",
    """
    MATCH (a:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity)-[:Has_text]->(name:Term)
    WHERE
        a.journalName IN ['biorxiv', 'medrxiv']
        AND entity.category = 'assay'
        AND t.category = 'assay'
        AND size(name.text) > 1  // exclude embarassing artefacts of the not so AI engine
    RETURN
        // keep only necessary fields and ndoe ids to minimze memory requirements
        a.doi AS doi,
        id(p) AS panel_id,
        id(t) AS t_id,
        name
    """,
    """
    WITH doi, panel_id, t_id, name
    // link to entity network
    MATCH (name)<-[:Has_text]-(bridge:H_Entity)
    WHERE bridge.category = 'assay'
    // find respective concept id
    WITH
        doi,
        panel_id,
        name,
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
    MATCH (paper:VizPaper {doi: doi})
    WITH paper, name_in_this_paper
    MERGE (entity:VizEntity {text: name_in_this_paper, category: 'assay'})
    MERGE (paper)-[:HasEntity]->(entity)
    RETURN COUNT(DISTINCT entity) AS `linked assays for visualization`
    """,
)


link_geneprod = UpdateOrCreateTask(
    "linking geneprods for visualization",
    """
    MATCH (a:SDArticle)-[:has_fig]->(f:SDFigure)-[:has_panel]->(p:SDPanel)-[:HasCondTag]->(t:CondTag)-[:Identified_by]->(entity:H_Entity)-[:Has_text]->(name:Term)
    WHERE
        a.journalName IN ['biorxiv', 'medrxiv']
        AND entity.type IN ['gene', 'protein', 'geneprod']
        AND t.type IN ['gene', 'protein', 'geneprod']
        AND (size(name.text) > 1 OR name.text = 's' )  // exclude embarassing artefacts of the not so AI engine but keep spike S SARS protein
    RETURN
        // keep only necessary fields and ndoe ids to minimze memory requirements
        a.doi AS doi,
        id(p) AS panel_id,
        id(t) AS t_id,
        name,
        entity
    """,
    """
    WITH doi, panel_id, t_id, name, entity
    // link to entity network
    MATCH (name)<-[:Has_text]-(bridge:H_Entity)
    // geneprod or  protein or genes
    WHERE bridge.type IN ['gene', 'protein', 'geneprod']
    // find respective concept id
    WITH
        doi,
        panel_id,
        name,
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
    MATCH (paper:VizPaper {doi: doi})
    WITH paper, name_in_this_paper
    MERGE (entity:VizEntity {text: name_in_this_paper, category: 'entity'})
    MERGE (paper)-[:HasEntity]->(entity)
    RETURN COUNT(DISTINCT entity) AS `linked geneprod for visualization`
    """,
)


auto_topics_highlights = SimpleDbTask(
    "highlighted topic entities",
    """
    // create VizCollection and VizSubCollection and attach VizEntity
    MATCH (topics_collection:SDAutoTopics)
    WITH
        topics_collection,
        id(topics_collection) AS topic_id,
        apoc.text.join(topics_collection.topics, ', ') AS topics_name
    MERGE (subcol:VizSubCollection {topics: topics_collection.topics, name: topics_name, topic_id: topic_id})
    WITH
        topics_collection,
        subcol
    MATCH (topics_collection)-->(highlighted_topic_entity:H_Entity)
    MERGE (highlight:VizEntity {text: highlighted_topic_entity.name, category: 'entity'})
    MERGE (subcol)-[:HasEntity {highlight_score: highlighted_topic_entity.community_centrality}]->(highlight)
    MERGE (col:VizCollection {name: 'by-auto-topics'})-[:HasSubCol]->(subcol)
    RETURN COUNT(DISTINCT highlight) AS `highlighted topic entities`
    """,
)


link_papers_to_highlights = SimpleDbTask(
    "linking papers to highlights",
    """
    MATCH (vizsubcol:VizSubCollection), (sdcol:SDAutoTopics)
    WHERE  vizsubcol.topic_id = id(sdcol)
    WITH vizsubcol, sdcol
    MATCH (sdcol)-->(a:SDArticle)
    WITH vizsubcol, a.doi AS doi
    MATCH (vzp:VizPaper {doi: doi})
    //highlight entities that overlap between paper and topic highlights
    WITH vizsubcol, vzp
    MATCH
    (vzp:VizPaper)-[:HasEntity]->(overlapping_entity:VizEntity {category: 'entity'})<-[:HasEntity]-(vizsubcol)
    WITH
        vizsubcol,
        vzp, 
        COLLECT(DISTINCT overlapping_entity) AS overlapping_highlights,
        COUNT(DISTINCT overlapping_entity) AS N_overlap
    WHERE N_overlap >= 2
    WITH
        vizsubcol,
        vzp,
        overlapping_highlights,
        N_overlap
    UNWIND overlapping_highlights AS paper_topic_highlight
    WITH
        vizsubcol,
        vzp,
        paper_topic_highlight,
        N_overlap
    MERGE (vzp)-[highlight_rel:HasEntityHighlight]->(paper_topic_highlight)
    MERGE (vizsubcol)-[r:HasPaper {overlap_size: N_overlap}]->(vzp)
    RETURN COUNT(DISTINCT r) AS `papers linked to highlighted topics`
    """,
)


create_automagic_collection = SimpleDbTask(
    "papers in the automagic set",
    """
    MATCH (a:SDArticle)
    // recent papers
    WHERE
        a.journalName IN ['biorxiv', 'medrxiv']
        AND DATETIME(a.pub_date) > (DATETIME() - duration({months: 2}))
    WITH a.doi AS doi
    // IMPORTANT: when in a tie, preprints will still be ordered by pub date
    ORDER BY DATETIME(a.pub_date) DESC
    LIMIT 5000
    MATCH (viza:VizPaper {doi: doi})-[:HasEntity]->(assay:VizEntity {category: 'assay'})
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
        COLLECT(DISTINCT [viza, assays]) AS preprint_list,
        COUNT(DISTINCT viza) AS N
    UNWIND range(0, N-1) as i
    // multiple preprints with same N_assays can have the same rank (tie)
    //UNWIND preprint_list_of_lists[i] AS preprint
    WITH COLLECT({rank: i, preprint: preprint_list[i]}) AS ranked_by_assays

    // rank by entities
    MATCH (a:SDArticle)
    WHERE
        a.journalName IN ['biorxiv', 'medrxiv']
        AND DATETIME(a.pub_date) > (DATETIME() - duration({months: 2}))
    WITH
        ranked_by_assays,
        a.doi AS doi
    // IMPORTANT: when ties, preprint will still be ordered by pub date...  
    ORDER BY DATETIME(a.pub_date) DESC
    LIMIT 5000
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
    MATCH (a:SDArticle)
    // recent papers
    WHERE
        a.journalName IN ['biorxiv', 'medrxiv']
        AND DATETIME(a.pub_date) > (DATETIME() - duration({months: 2}))
    WITH
        ranked_by_assays,
        ranked_by_entities,
        a.doi AS doi
    ORDER BY DATETIME(a.pub_date) DESC
    LIMIT 5000
    MATCH (col:VizCollection {name: "by-auto-topics"})-->(topic:VizSubCollection)-[rel_autotopics_paper]->(viza:VizPaper {doi: doi})
    WHERE rel_autotopics_paper.overlap_size >= 2
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        viza,
        COUNT(DISTINCT topic) AS N_topics,
        COLLECT(DISTINCT topic.name) AS topics
    // IMPORTANT: when ties, preprint will still be ordered by pub date...  
    ORDER BY N_topics DESC
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        COLLECT(DISTINCT [viza, topics]) AS preprint_list,
        COUNT(DISTINCT viza) AS N
    UNWIND range(0, N-1) AS i
    WITH
        ranked_by_assays,
        ranked_by_entities,
        COLLECT({rank:i, preprint: preprint_list[i]}) AS ranked_by_topics

    // rank by presence of peer reviews
    MATCH (col:VizCollection {name: "refereed-preprints"})-->(sub:VizSubCollection)-->(viza:VizPaper)

    // recent papers
    WHERE DATETIME(viza.pub_date) > (DATETIME() - duration({months: 2}))
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        ranked_by_topics,
        viza
    OPTIONAL MATCH (:Article {doi: viza.doi})-[:HasReview]->(review:Review)
    OPTIONAL MATCH (:Article {doi: viza.doi})-[:HasAnnot]->(annot:PeerReviewMaterial)
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        ranked_by_topics,
        viza,
        CASE
            WHEN EXISTS(review.reviewed_by) THEN review.reviewed_by
            ELSE annot.reviewed_by
        END AS reviewed_by
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        ranked_by_topics,
        viza,
        COLLECT(DISTINCT reviewed_by) AS reviewers
    WITH DISTINCT
        ranked_by_assays,
        ranked_by_entities,
        ranked_by_topics,
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
        preprint,
        N_ranks,
        ranks,
        stuff,
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
    RETURN COUNT(DISTINCT preprint) AS `papers in the automagic set`
    """,
)


Tasks = purge_viz_graph_tasks + [
    create_sd_articles,
    create_viz_papers,
    create_by_rev_service_collections,
    link_exp_assays,
    link_geneprod,
    auto_topics_highlights,
    link_papers_to_highlights,
    create_automagic_collection,
]


if __name__ == "__main__":
    configure_logging()
    run_flow(DB, Tasks, "precomputing the viz graph")
