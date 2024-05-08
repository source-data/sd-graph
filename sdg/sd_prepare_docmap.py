"""Graph processing pipeline."""

from common.logging import configure_logging
from neotools.flow import (
    DetachDeleteAll,
    run_flow,
    UpdateOrCreateTask,
)
from sdg import DB, EEB_PUBLIC_API

DOCMAPS_API_URL = EEB_PUBLIC_API + "docmaps/v1/docmap/"
DOI_URL = "https://doi.org/"

purge_docmap_graph_tasks = [
    DetachDeleteAll("Resource"),
    DetachDeleteAll("Docmap"),
    DetachDeleteAll("Preprint"),
    DetachDeleteAll("RefereeReport"),
    DetachDeleteAll("AuthorReply"),
    DetachDeleteAll("PublishedArticle"),
    DetachDeleteAll("Person"),
    DetachDeleteAll("Creator"),
    DetachDeleteAll("Content"),
    DetachDeleteAll("Assertion"),
    DetachDeleteAll("Action"),
    DetachDeleteAll("Step"),
    DetachDeleteAll("WebPage"),
]


create_preprint_docmaps = UpdateOrCreateTask(
    "creating Docmaps from biorxiv/medrxiv preprints",
    """
    MATCH (rs:ReviewingService)
    WITH rs
    MATCH (a:Article)
    OPTIONAL MATCH (a)-[:HasReview]->(review:Review {reviewed_by: rs.name})
    WITH rs, a, review
    OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: rs.name})
    WITH rs, a, review, annot
    WHERE
        (review is NOT NULL OR annot IS NOT NULL)
        AND a.journal_title IN ['bioRxiv', 'medRxiv']
    WITH DISTINCT rs, a.doi as doi, a.publication_date as published
    ORDER BY DATETIME(published)
    // keep oldest published date
    RETURN DISTINCT rs, doi, COLLECT(published)[0] as published
    """,
    """
    WITH rs, doi, published, '_:b-'+apoc.create.uuid() as first_step
    MERGE (preprint:Preprint {
        uri: 'https://doi.org/' + doi,
        doi: doi,
        published: toString(DATETIME(published))
    })
    MERGE (docmap:Docmap {
        type: 'docmap',
        created: toString(DATETIME()),
        generatedAt: toString(DATETIME()),
        provider: 'https://eeb.embo.org',
        publisher_url: rs.url,
        publisher_name: rs.name,
        publisher_peer_review_policy: rs.peer_review_policy,
        id: '%(docmaps_api_url)s' + doi + '/' + apoc.text.snakeCase(apoc.text.clean(rs.name)),
        first_step: first_step
    })
    MERGE (docmap)<-[:steps]-(step:Step {id: first_step})
    MERGE (step)<-[:inputs]-(preprint)
    """ % {"docmaps_api_url": DOCMAPS_API_URL},
)


create_referee_report_actions = UpdateOrCreateTask(
    "creating Docmap actions for referee reports",
    """
    MATCH (rs:ReviewingService)
    WITH rs
    MATCH (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(step:Step)<-[:inputs]-(preprint:Preprint)
    OPTIONAL MATCH (a:Article {doi: preprint.doi})-[r:HasReview]->(review:Review {reviewed_by: rs.name})
    WITH rs, docmap, step, preprint, review
    OPTIONAL MATCH (a:Article {doi: preprint.doi})-[r:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: rs.name})
    // use aggregation to coerce individual peer review material documents as review
    RETURN DISTINCT
        preprint.uri AS preprint_uri,
        preprint.doi AS doi,
        docmap,
        step,
        COLLECT(DISTINCT review) + COLLECT(DISTINCT annot) AS reviews
    """,
    """
    WITH preprint_uri, doi, docmap, step, reviews
    UNWIND reviews as review
    WITH DISTINCT
        preprint_uri,
        doi,
        docmap,
        step,
        review,
        '_:b-'+apoc.create.uuid() AS action_uuid,
        // filtering NULLs to prevent error in MERGE
        CASE WHEN review.doi IS NOT NULL
            THEN '%(doi_url)s' + review.doi
            ELSE 'https://biorxiv.org/content/' + doi + '#review'
        END AS web_page_link
    MERGE (step)<-[:assertions]-(assertion:Assertion {
        item: preprint_uri,
        status: 'reviewed'
    })
    MERGE (step)<-[:actions]-(action:Action {id: action_uuid})
    MERGE (action)<-[:outputs]-(rev:RefereeReport {
        published: review.posting_date,
        type: 'review',
        uri: web_page_link
    })
    // review.doi and .runningNumber can be null and must therefore be set outside the merge query
    ON CREATE SET
        rev.doi = review.doi,
        rev.runningNumber = review.review_idx
    // realization on eeb as json
    MERGE (rev)<-[:content]-(content_on_eeb:Content {
        type: 'web-page',
        url: web_page_link
    })
    MERGE (rev)<-[:content]-(:Content {
        type: 'text',
        text: review.text
    })
    WITH DISTINCT action, review
    WHERE review.review_idx IS NOT NULL
    MERGE (action)<-[:participants]-(reviewer:Person {
        id : 'reviewer #' + review.review_idx,
        name: 'anonymous',
        role: 'peer-reviewer'
    })
    SET action.index = review.review_idx
    """ % {
        "doi_url": DOI_URL,
    },
)


create_review_summary_action = UpdateOrCreateTask(
    "creating Docmap action for review summaries",
    """
    MATCH
        (rs:ReviewingService),
        (:Docmap {publisher_url: rs.url})<-[:steps]-(step:Step)<-[:inputs]-(preprint:Preprint),
        (:Article {doi: preprint.doi})-[:HasReview]->(:Review {reviewed_by: rs.name})-[:HasSummary]->(summary:Summary)
    RETURN DISTINCT step, summary
    """,
    """
    WITH step, summary
    MERGE (step)<-[:actions]-(action:Action {id: '_:b-'+apoc.create.uuid()})
    MERGE (action)<-[:outputs]-(revSummary:RefereeReportsSummary {
        published: apoc.temporal.format(summary.created_at, 'ISO_LOCAL_DATE_TIME'),
        type: 'reviews-summary'
    })
    MERGE (revSummary)<-[:content]-(:Content {
        type: 'text', 
        text: summary.summary_text,
        id: toString(id(summary)),
        service: 'https://eeb.embo.org/'
    })
    """,
)


create_response_actions = UpdateOrCreateTask(
    "creating Docmaps actions for responses to referee reports",
    """
    MATCH (rs:ReviewingService)
    WITH rs
    MATCH
        (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(reviewing_step:Step)<-[:actions]-(:Action)<-[:outputs]-(review:RefereeReport),
        (reviewing_step)<-[:inputs]-(preprint:Preprint),
        (a:Article {doi: preprint.doi})-[:HasResponse]->(response:Response {reviewed_by: rs.name})
    RETURN DISTINCT
        preprint.uri AS preprint_uri,
        preprint.doi AS doi,
        docmap,
        reviewing_step,
        COLLECT(DISTINCT review) AS reviews,
        response
    """,
    """
    WITH
        preprint_uri,
        doi,
        docmap,
        reviewing_step,
        reviews,
        response,
        '_:b-'+apoc.create.uuid() as reply_step
    SET reviewing_step.next_step = reply_step
    MERGE (docmap)<-[:steps]-(step:Step {id: reply_step, previous_step: reviewing_step.id})
    MERGE (step)<-[:assertions]-(assertion:Assertion {
        item: preprint_uri,
        status: '' // in the future: a value to the effect that 'authors-replied-to-reviewers'
    })
    WITH DISTINCT doi, docmap, reviews, response, step
    UNWIND reviews as review
    WITH DISTINCT doi, docmap, review, response, step
    MERGE (step)<-[:inputs]-(review)
    WITH DISTINCT doi, docmap, response, step
    WITH
        doi,
        docmap,
        response,
        step,
        '_:b-'+apoc.create.uuid() AS action_uuid,
        CASE WHEN response.doi IS NOT NULL
            THEN '%(doi_url)s' + response.doi
            ELSE 'https://biorxiv.org/content/' + doi + '#review'
        END AS web_page_link
    MERGE (step)<-[:actions]-(action:Action {id: action_uuid})
    MERGE (action)<-[:outputs]-(reply:AuthorReply {
        published: response.posting_date,
        type: 'author-response',
        uri: web_page_link
    })
    // as above with reviews, response.doi can be null and must be set outside the merge query
    ON CREATE SET reply.doi = response.doi
    MERGE (reply)<-[:content]-(content:Content {
        type: 'web-page',
        url: web_page_link
    })
    MERGE (reply)<-[:content]-(:Content {
        type: 'text',
        text: response.text
    })
    """ % {
        "doi_url": DOI_URL,
    },
)


create_participants = UpdateOrCreateTask(
    "creating Docmap participants for authors",
    """
    MATCH (rs:ReviewingService)
    WITH rs
    MATCH
        (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(replying_step:Step)<-[:actions]-(reply_action:Action)<-[:outputs]-(reply:AuthorReply),
        (docmap)<-[:steps]-(reviwing_step:Step)<-[:inputs]-(preprint:Preprint)
    WITH DISTINCT docmap, preprint, reply_action
    MATCH (a:Article {doi: preprint.doi})-[:has_author]->(author:Contrib)
    OPTIONAL MATCH (author)-[:has_orcid]->(orcid:Contrib_id)
    RETURN DISTINCT
        reply_action,
        author,
        preprint,
        CASE 
            WHEN orcid IS NULL THEN 'null'
            ELSE orcid.text
        END AS orcid
    """,
    """
    WITH
        reply_action,
        author,
        preprint,
        orcid
    MERGE (reply_action)<-[:participants]-(person:Person {
        identifier: orcid,
        firstName: author.given_names,
        familyName: author.surname,
        role: 'author'
    })
    MERGE (preprint)-[:has_author]->(person)
    """,
)


create_published_article_docmaps = UpdateOrCreateTask(
    "creating Docmaps for published articles",
    """
MATCH (a:Article)
WHERE
    // these are fields needed to construct the new docmap.
    a.journal_doi IS NOT NULL
    AND a.published_journal_title IS NOT NULL
    AND a.publication_date IS NOT NULL
MATCH (Docmap)<-[:steps]-(Step)<-[:inputs]-(preprint:Preprint {doi: a.doi})
WITH DISTINCT
    preprint,
    a.publication_date as preprint_publication_date,
    a.journal_doi as published_article_doi,
    apoc.convert.toString(a.published_journal_title) as publisher_title,
    a.published_date as published_date
// order by and collect to get the newest version
ORDER BY DATETIME(preprint_publication_date)
RETURN DISTINCT
    preprint,
    COLLECT(preprint_publication_date)[0] as preprint_publication_date,
    published_article_doi,
    publisher_title,
    published_date
    """,
    """
    WITH
        preprint,
        preprint_publication_date,
        published_article_doi,
        publisher_title,
        published_date,
        '_:b-'+apoc.create.uuid() as id_step,
        '_:b-'+apoc.create.uuid() AS id_action
    MERGE (docmap:Docmap {
        type: 'docmap',
        provider: 'https://eeb.embo.org',
        publisher_name: publisher_title,
        id: '%(docmaps_api_url)s' + preprint.doi + '/' + apoc.text.snakeCase(apoc.text.clean(publisher_title))
    })
    // if no docmap for this publisher exists, set the necessary properties
    ON CREATE SET
        docmap.created = toString(DATETIME()),
        docmap.generatedAt = toString(DATETIME()),
        docmap.first_step = id_step
    MERGE (docmap)<-[:steps]-(step:Step {id: id_step})
    MERGE (step)<-[:inputs]-(preprint)
    MERGE (step)<-[:assertions]-(assertion:Assertion {
        item: preprint.uri,
        status: 'published'
    })
    MERGE (step)<-[:actions]-(action:Action {id: id_action})
    MERGE (action)<-[:outputs]-(pub:PublishedArticle {
        doi: published_article_doi,
        type: 'journal-publication',
        uri: 'https://doi.org/' + published_article_doi
    })
    ON CREATE SET
        pub.published = toString(DATETIME(published_date))
    MERGE (rev)<-[:content]-(content:Content {
        type: 'web-page',
        url: pub.uri,
        id: published_article_doi,
        service: 'https://doi.org/'
    })
    """ % {"docmaps_api_url": DOCMAPS_API_URL},
)


Tasks = purge_docmap_graph_tasks + [
    create_preprint_docmaps,
    create_referee_report_actions,
    create_review_summary_action,
    create_response_actions,
    create_participants,
    create_published_article_docmaps,
]


if __name__ == "__main__":
    configure_logging()
    run_flow(DB, Tasks, "creating the docmap graph")
