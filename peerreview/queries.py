from neotools.db import Query


class MATCH_DOI(Query):
    code = """MATCH (a:Article {doi: $doi}) RETURN DISTINCT a"""
    returns = ["a"]


class NotYetPublished(Query):
    code = """
MATCH (a:Article)
WHERE
    a.publication_date IS NOT NULL
    AND a.publication_date <> ""
    AND (DATETIME(a.publication_date) > DATETIME($limit_date))
    AND NOT EXISTS(a.journal_doi)
RETURN DISTINCT a.doi AS doi
    """
    map = {"limit_date": []}
    returns = ["doi"]


class PublishedNoDate(Query):
    code = """
MATCH (a:Article)
WHERE EXISTS(a.journal_doi) AND NOT EXISTS(a.published_date)
RETURN DISTINCT a.doi AS preprint_doi, a.journal_doi AS published_doi
    """
    returns = ["preprint_doi", "published_doi"]


class UpdatePublicationStatus(Query):
    code = """
MATCH (a:Article {doi: $preprint_doi})
SET
    a.journal_doi = $published_doi,
    a.published_journal_title = $published_journal_title,
    a.published_date = $published_date
RETURN a
    """
    map = {
        "preprint_doi": [],
        "published_doi": [],
        "published_journal_title": [],
        "published_date": [],
    }
    returns = ["a"]


class LINK_REVIEWS(Query):
    code = """
MATCH (review:Review), (a:Article)
WHERE review.related_article_doi = a.doi
WITH review, a
MERGE (a)-[r:HasReview]->(review)
RETURN COUNT(DISTINCT r) AS N
    """
    returns = ["N"]


class LINK_RESPONSES(Query):
    code = """
MATCH (response:Response), (a:Article)
WHERE response.related_article_doi = a.doi
WITH response, a
MERGE (a)-[r:HasResponse]->(response)
RETURN COUNT(DISTINCT r) AS N
    """
    returns = ["N"]


class LINK_ANNOT(Query):
    code = """
MATCH (annot:PeerReviewMaterial), (a:Article)
WHERE annot.related_article_doi = a.doi
WITH annot, a
MERGE (a)-[r:HasAnnot]->(annot)
RETURN COUNT(DISTINCT r) AS N
    """
    returns = ["N"]


class REFEREED_PREPRINTS_POSTED_AFTER(Query):
    code = """
MATCH (a:Article)
MATCH (a)-[:HasReview]->(review:Review)
WHERE review.posting_date >= $after AND review.reviewed_by = $reviewed_by
RETURN DISTINCT a.doi AS doi
    """
    map = {"after": [], "reviewed_by": []}
    returns = ["doi"]


class REVIEWS_WITHOUT_SUMMARIES(Query):
    code = """
MATCH (r:Review)
WHERE
    r.reviewed_by = $reviewed_by
    AND r.text_significance IS NOT NULL
    AND NOT((r)-[:HasSummary]->(:Summary))
WITH r.related_article_doi AS article_doi
MATCH (r:Review {related_article_doi: article_doi})
WITH article_doi, r
ORDER BY r.review_idx ASC
RETURN article_doi, COLLECT(DISTINCT r) AS reviews
    """
    map = {"reviewed_by": []}
    returns = ["article_doi", "reviews"]


class CREATE_SUMMARY(Query):
    code = """
MATCH (summarization_config:SummarizationConfig)
WHERE ID(summarization_config) = $id_summarization_config

CREATE (summary:Summary {
    reviews_text: $reviews_text,
    summary_text: $summary_text,
    created_at: datetime()
})
CREATE (summary)-[:GeneratedWith]->(summarization_config)

WITH summary, $article_doi AS article_doi
MATCH (:Article {doi: article_doi})-[:HasReview]->(review:Review)
MERGE (review)-[:HasSummary]->(summary)

RETURN summary
    """
    map = {
        "article_doi": [],
        "reviews_text": [],
        "summary_text": [],
        "id_summarization_config": [],
    }
    returns = ["summary"]


class MERGE_SUMMARIZATION_CONFIG(Query):
    code = """
MERGE (summarization_config:SummarizationConfig {
    parameters: $parameters,
    prompt: $prompt
})
ON CREATE SET summarization_config.created_at = datetime()
RETURN summarization_config
    """

    map = {
        "parameters": [],
        "prompt": [],
    }
    returns = ["summarization_config"]
