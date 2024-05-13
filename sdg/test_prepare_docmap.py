from neotools.db import Query
from neotools.flow import run_flow
from sdg.sd_prepare_docmap import Tasks as PrepareDocmapTasks
from tests.utils import DbTestCase


class CreateReviewService(Query):
    name = "Review Commons"
    peer_review_policy = "https://reviewcommons.org/for-reviewers"
    url = "https://reviewcommons.org"

    code = """
    CREATE (revService:ReviewingService {
        name: "%s",
        url: "%s",
        peer_review_policy: "%s"
    })
    """ % (name, url, peer_review_policy)


class CreateArticle(Query):

    def __init__(self, article, peer_review_materials, reviews, responses):
        params = {
            "doi": article["doi"],
            "journal_title": article["journal_title"],
            "publication_date": article["publication_date"],
            "title": article["title"],
        }
        self.code = """CREATE (a:Article {
            doi: $doi,
            journal_title: $journal_title,
            publication_date: $publication_date,
            title: $title
        })
        """

        def _cypher_for_article_relationship(
            relationship_type,
            node_type,
            node_idx,
            node_attributes,
        ):
            param_name_base = f"{node_type.lower()}_{node_idx}"
            params = {
                f"{param_name_base}__{key}": value
                for key, value in node_attributes.items()
            }
            cypher_attrs = "{ " + ", ".join([
                f"{key}: ${param_name_base}__{key}"
                for key in node_attributes.keys()
            ]) + " }"
            code = f"CREATE (a)-[:{relationship_type}]->(:{node_type} {cypher_attrs})"
            return code, params

        for i, review in enumerate(reviews):
            review_code, review_params = _cypher_for_article_relationship("HasReview", "Review", i, review)
            params.update(review_params)
            self.code += review_code
        for i, peer_review_material in enumerate(peer_review_materials):
            peer_review_material_code, peer_review_material_params = _cypher_for_article_relationship("HasAnnot", "PeerReviewMaterial", i, peer_review_material)
            params.update(peer_review_material_params)
            self.code += peer_review_material_code
        for i, response in enumerate(responses):
            response_code, response_params = _cypher_for_article_relationship("HasResponse", "Response", i, response)
            params.update(response_params)
            self.code += response_code
        super().__init__(params=params)


class VerifyDocmapPresent(Query):

    def __init__(self, doi, publication_date, present):
        self.good_result = f"Docmap {'present' if present else 'not present'} for {doi} published on {publication_date}"
        params = {
            "doi": doi,
            "publication_date": publication_date,
            "present": 1 if present else 0,
            "good_result": self.good_result,
        }
        super().__init__(params=params)

    code = """
    MATCH (p:Preprint {
        doi: $doi,
        published: toString(DATETIME($publication_date))
    })
    MATCH (p)-[:inputs]->(:Step)-[:steps]->(:Docmap)
    WITH COUNT(*) AS count
    RETURN
        CASE WHEN count = $present
            THEN $good_result
            ELSE "Failed: " + $good_result + ". Expected " + $present + " Docmap but got " + count
        END AS result
    """

class VerifyReviewContentPresent(Query):

    def __init__(self, doi, publication_date, review_data):
        self.good_result = f"Docmap for {doi} published on {publication_date} has correct review content"
        review_doi = review_data["doi"]
        review_uri = f"https://doi.org/{review_doi}" if review_doi else f"https://biorxiv.org/content/{doi}#review"
        params = {
            "doi": doi,
            "publication_date": publication_date,
            "review_doi": review_doi,
            "review_posting_date": review_data["posting_date"],
            "review_idx": review_data["review_idx"],
            "review_text": review_data["text"],
            "review_uri": review_uri,
            "n_reviews_expected": 1,
            "good_result": self.good_result,
        }
        super().__init__(params=params)

    code = """
    MATCH (p:Preprint {
        doi: $doi,
        published: toString(DATETIME($publication_date))
    })
    MATCH
        (p)-[:inputs]->(:Step)<-[:actions]-(:Action)<-[:outputs]-(r:RefereeReport {
            doi: $review_doi,
            published: $review_posting_date,
            runningNumber: $review_idx,
            type: 'review',
            uri: $review_uri
        }),
        (r)<-[:content]-(c1:Content {
            text: $review_text,
            type: "text"
        }),
        (r)<-[:content]-(c2:Content {
            type: "web-page",
            url: $review_uri
        })
    OPTIONAL MATCH (r)<-[:content]-(other_c:Content)
    WHERE other_c <> c1 AND other_c <> c2
    WITH COUNT(DISTINCT r) AS n_reviews, COUNT(DISTINCT other_c) AS n_other_contents
    RETURN
        CASE WHEN n_reviews = $n_reviews_expected AND n_other_contents = 0
            THEN $good_result
            ELSE "Failed: " + $good_result + ". Expected " + $n_reviews_expected + " RefereeReport node(s) with 2 Content nodes but got " + n_reviews + " RefereeReport node(s) with " + n_other_contents + " additional Content node(s)"
        END AS result
    """

def _valid_day_of_month(day):
    return min(28, max(1, day))

def _article_data(i):
    return {
        "doi": f"10.1234/{i:02}",
        "journal_title": "bioRxiv",
        "publication_date": f"2020-01-{_valid_day_of_month(i):02}",
        "title": "Article {i:02}",
    }

def _review_data(i):
    return {
        "doi": f"10.1234/review-{i:02}",
        "hypothesis_id": f"hypo-id-review-{i:02}",
        "link_html": f"https://hypothes.is/link-to/hypo-id-review-{i:02}",
        "posting_date": f"2021-01-{_valid_day_of_month(i):02}",
        "review_idx": f"{i}",
        "reviewed_by": CreateReviewService.name,
        "text": f"Text for review {i:02}",
    }

def _prm_data(i):
    return {
        "doi": f"10.1234/prm-{i:02}",
        "hypothesis_id": f"hypo-id-prm-{i:02}",
        "link_html": f"https://hypothes.is/link-to/hypo-id-prm-{i:02}",
        "posting_date": f"2021-02-{_valid_day_of_month(i):02}",
        "reviewed_by": CreateReviewService.name,
        "text": f"Text for peer review material {i:02}",
    }

def _response_data(i):
    return {
        "doi": f"10.1234/response-{i:02}",
        "hypothesis_id": f"hypo-id-response-{i:02}",
        "link_html": f"https://hypothes.is/link-to/hypo-id-response-{i:02}",
        "posting_date": f"2021-03-{_valid_day_of_month(i):02}",
        "reviewed_by": CreateReviewService.name,
        "text": f"Text for response {i:02}",
    }


class DocmapTestCase(DbTestCase):

    def setUp(self):
        super().setUp()
        self.db.query(CreateReviewService())

    def run_prepare_docmap(self):
        run_flow(self.db, PrepareDocmapTasks, "test_prepare_docmap")

    def test_docmaps_are_created(self):
        article_fixtures = [
            (
                [
                    _article_data(1),
                    [],  # no reviews
                    [],  # no peer review materials
                    [],  # no responses
                ],
                False,  # => no docmap
            ),
            (
                [
                    _article_data(2),
                    [_review_data(1)],  # one review
                    [],  # no peer review materials
                    [],  # no responses
                ],
                True,  # => docmap
            ),
            (
                [
                    _article_data(3),
                    [],  # no reviews
                    [_prm_data(1)],  # one peer review material
                    [],
                ],
                True,  # => docmap
            ),
            (
                [
                    _article_data(4),
                    [],  # no reviews
                    [],  # no peer review materials
                    [_response_data(1)],  # one response
                ],
                False,  # => no docmap
            ),
            (
                [
                    _article_data(5),
                    [_review_data(2)],  # one review
                    [_prm_data(2)],  # one peer review material
                    [],  # no response
                ],
                True,  # => docmap
            ),
        ]
        for args, _ in article_fixtures:
            self.db.query(CreateArticle(*args))

        self.run_prepare_docmap()

        for args, docmap_present in article_fixtures:
            article_data = args[0]
            verify_query = VerifyDocmapPresent(article_data["doi"], article_data["publication_date"], docmap_present)
            self.assertEqual(
                verify_query.good_result,
                self.db.query(verify_query)[0][0],
                msg="The database graph is not as expected.",
            )

    def test_action_contents_are_created(self):
        article_data = _article_data(1)
        review_data = _review_data(1)

        self.db.query(CreateArticle(article_data, [review_data], [], []))
        self.run_prepare_docmap()

        verify_query = VerifyReviewContentPresent(article_data["doi"], article_data["publication_date"], review_data)
        self.assertEqual(
            verify_query.good_result,
            self.db.query(verify_query)[0][0],
            msg="The database graph is not as expected",
        )
