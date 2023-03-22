from os import getenv
from unittest import TestCase
from unittest.mock import call, patch

from neotools.db import Instance, Query
import peerreview.summarization


class DbTestCase(TestCase):
    class DeleteAll(Query):
        code = "MATCH (n) DETACH DELETE n"

    class NumNodesInDatabase(Query):
        code = "MATCH (n) RETURN COUNT(n) AS N"
        returns = ["N"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Instance(
            getenv("NEO_URI"), getenv("NEO_USERNAME"), getenv("NEO_PASSWORD")
        )

    def setUp(self):
        self.verify_database_empty()

    def tearDown(self):
        self.db.query(self.__class__.DeleteAll())

    def verify_database_empty(self):
        num_nodes_in_database = self.db.query(self.__class__.NumNodesInDatabase())[0][0]
        self.assertEqual(
            0,
            num_nodes_in_database,
            msg="The database must empty before running tests.",
        )


review_texts = {
    "a1": {
        "reviews": [
            """This is the start of the review. Here's the significance:
#### Significance
**Major Points**
Significance of review #1 of the psychoceramics of Theory.""",
            """#### Significance
Significance of review #2 of the psychoceramics of Theory.
**Referee cross-commenting**
This referee cross-commenting must be removed.""",
            """#### Significance
see above""",
        ],
        "concated": """Review #1:
Major Points
Significance of review #1 of the psychoceramics of Theory.

Review #2:
Significance of review #2 of the psychoceramics of Theory.""",
    },
    "a2": {
        "reviews": [
            """This is the start of the review. Here's the significance:
#### Significance
Significance of review #1 of the psyceramics of Chotheory.""",
            """#### Significance
Significance of review #2 of the psyceramics of Chotheory.""",
        ],
        "concated": """Review #1:
Significance of review #1 of the psyceramics of Chotheory.

Review #2:
Significance of review #2 of the psyceramics of Chotheory.""",
    },
    "a3": {
        "reviews": [
            """This is the start of the review. While the review mentions significance,
there is markdown heading of that name so this review should not be used.""",
            """This review also has no significance section.""",
        ],
        "concated": None,
    },
}


MockSummaryText = "A mock summary of some reviews."


class CreateSummarizationFixtures(Query):
    """Creates the article-with-reviews fixtures needed to test the summarization step.

    1. Article 1 has 3 reviews: 2 with significance sections that contain markdown and
    need to be filtered, 1 with a significance section that is too short and needs to be
    removed.
    2. There are two versions of article 2, which have 2 reviews with significance
    sections.
    3. Article 3 has 2 reviews without significance sections.
    """

    def __init__(self):
        super().__init__(
            params={
                "a1_r1": review_texts["a1"]["reviews"][0],
                "a1_r2": review_texts["a1"]["reviews"][1],
                "a1_r3": review_texts["a1"]["reviews"][2],
                "a2_r1": review_texts["a2"]["reviews"][0],
                "a2_r2": review_texts["a2"]["reviews"][1],
                "a3_r1": review_texts["a3"]["reviews"][0],
                "a3_r2": review_texts["a3"]["reviews"][1],
            }
        )

    code = """
    CREATE (a1:Article {doi: "10.1234/567890"})
    CREATE (a1)-[:HasReview]->(:Review {
        related_article_doi: a1.doi,
        reviewed_by: "review commons",
        review_idx: 1,
        text: $a1_r1
    })
    CREATE (a1)-[:HasReview]->(:Review {
        related_article_doi: a1.doi,
        reviewed_by: "review commons",
        review_idx: 2,
        text: $a1_r2
    })
    CREATE (a1)-[:HasReview]->(:Review {
        related_article_doi: a1.doi,
        reviewed_by: "review commons",
        review_idx: 3,
        text: $a1_r3
    })

    CREATE (a2v1:Article {doi: "10.asdf/ghjkl", version: "1"})
    CREATE (a2v2:Article {doi: a2v1.doi, version: "2"})
    CREATE (a1r1:Review {
        related_article_doi: a2v1.doi,
        reviewed_by: "review commons",
        review_idx: 1,
        text: $a2_r1
    })
    CREATE (a1r2:Review {
        related_article_doi: a2v1.doi,
        reviewed_by: "review commons",
        review_idx: 2,
        text: $a2_r2
    })
    CREATE (a2v1)-[:HasReview]->(a1r1)
    CREATE (a2v1)-[:HasReview]->(a1r2)
    CREATE (a2v2)-[:HasReview]->(a1r1)
    CREATE (a2v2)-[:HasReview]->(a1r2)

    CREATE (a3:Article {doi: "10.0987/654321"})
    CREATE (a3)-[:HasReview]->(:Review {
        related_article_doi: a3.doi,
        reviewed_by: "review commons",
        review_idx: 1,
        text: $a3_r1
    })
    CREATE (a3)-[:HasReview]->(:Review {
        related_article_doi: a3.doi,
        reviewed_by: "review commons",
        review_idx: 2,
        text: $a3_r2
    })
"""


class Verify1stArticleSummaryIsPresent(Query):
    def __init__(self):
        super().__init__(
            params={
                "reviews_text": review_texts["a1"]["concated"],
                "summary_text": MockSummaryText,
                "good_result": self.good_result,
            }
        )

    code = """
    MATCH (s:Summary {
        summary_text: $summary_text,
        reviews_text: $reviews_text
    })
    MATCH (s)-[:GeneratedWith]->(:SummarizationConfig)

    MATCH (a:Article {doi: "10.1234/567890"})
    MATCH (a)-[:HasReview]->(r1:Review {related_article_doi: a.doi, review_idx: 1})
    MATCH (a)-[:HasReview]->(r2:Review {related_article_doi: a.doi, review_idx: 2})
    MATCH (a)-[:HasReview]->(r3:Review {related_article_doi: a.doi, review_idx: 3})

    MATCH (r1)-[:HasSummary]->(s)
    MATCH (r2)-[:HasSummary]->(s)
    MATCH (r3)-[:HasSummary]->(s)

    RETURN
        CASE WHEN COUNT(*) = 1
            THEN $good_result
            ELSE "Failed: " + $good_result
        END AS result
    """
    good_result = "Summary for article 1 is correct."


class Verify2ndArticleSummaryIsPresent(Query):
    def __init__(self):
        super().__init__(
            params={
                "reviews_text": review_texts["a2"]["concated"],
                "summary_text": MockSummaryText,
                "good_result": self.good_result,
            }
        )

    code = """
    MATCH (s:Summary {
        summary_text: $summary_text,
        reviews_text: $reviews_text
    })
    MATCH (s)-[:GeneratedWith]->(:SummarizationConfig)

    MATCH (a_v1:Article {doi: "10.asdf/ghjkl", version: "1"})
    MATCH (a_v2:Article {doi: a_v1.doi, version: "2"})

    MATCH (r1:Review {related_article_doi: a_v1.doi, review_idx: 1})
    MATCH (r2:Review {related_article_doi: a_v1.doi, review_idx: 2})

    MATCH (r1)-[:HasSummary]->(s)<-[:HasSummary]-(r2)

    MATCH (a_v1)-[:HasReview]->(r1)<-[:HasReview]-(a_v2)
    MATCH (a_v1)-[:HasReview]->(r2)<-[:HasReview]-(a_v2)

    RETURN
        CASE WHEN COUNT(*) = 1
            THEN $good_result
            ELSE "Failed: " + $good_result
        END AS result
    """
    good_result = "Summary for article 2 is correct."


class Verify2SummariesGenerated(Query):
    def __init__(self):
        super().__init__(
            params={
                "good_result": self.good_result,
            }
        )

    code = """
    MATCH (s:Summary)-[:GeneratedWith]->(:SummarizationConfig)
    RETURN
        CASE WHEN COUNT(*) = 2
            THEN $good_result
            ELSE "Failed: " + $good_result
        END AS result
    """
    good_result = "Only summaries for 2 articles present."


VerifyGraphQueries = [
    Verify2SummariesGenerated(),
    Verify1stArticleSummaryIsPresent(),
    Verify2ndArticleSummaryIsPresent(),
]


class VerifyNoSummariesGenerated(Query):
    code = """
    MATCH (s:Summary)
    RETURN CASE WHEN COUNT(*) = 0 THEN "graph is good" ELSE "graph is bad" END AS result
    """
    good_result = "graph is good"


class SummarizationTestCase(DbTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_dir = "/app/mecadoi"

    @patch("peerreview.summarization.chat", return_value=MockSummaryText)
    def test_basic_summarization(self, chat_mock):
        self.create_summarization_fixtures()
        self.run_summarization()
        self.verify_chat_mock_calls(chat_mock)
        self.verify_summarization_results()

    @patch("peerreview.summarization.chat", return_value=MockSummaryText)
    def test_summarization_is_not_needlessly_repeated(self, chat_mock):
        self.create_summarization_fixtures()
        # Run summarization for the first time. Here, the chat mock should be called
        # (this is verified in the basic test)
        self.run_summarization()
        self.verify_chat_mock_calls(chat_mock)
        # Reset the mock so we can call assert_not_called() later
        chat_mock.reset_mock()
        self.run_summarization()
        # Verify that the expected results are in the database
        self.verify_summarization_results()
        # Verify that the chat mock was not called during the second summarization run
        chat_mock.assert_not_called()

    @patch("peerreview.summarization.chat", return_value=MockSummaryText)
    def test_dry_run_summarization(self, chat_mock):
        self.create_summarization_fixtures()
        self.run_summarization(dry_run=True)
        self.verify_chat_mock_calls(chat_mock, dry_run=True)
        self.verify_query_result(VerifyNoSummariesGenerated())

    def create_summarization_fixtures(self):
        self.db.query(CreateSummarizationFixtures())

    def run_summarization(self, dry_run=False):
        summarizer = peerreview.summarization.Summarizer(peerreview.summarization.DB)
        summarizer.run(self.input_dir, dry_run=dry_run)

    def verify_chat_mock_calls(self, chat_mock, dry_run=False):
        print(chat_mock.mock_calls)
        chat_mock.assert_has_calls(
            [
                call(
                    peerreview.summarization.review_summarization_prompt(
                        review_texts["a1"]["concated"]
                    ),
                    peerreview.summarization.review_summarization_parameters,
                    dry_run=dry_run,
                ),
                call(
                    peerreview.summarization.review_summarization_prompt(
                        review_texts["a2"]["concated"]
                    ),
                    peerreview.summarization.review_summarization_parameters,
                    dry_run=dry_run,
                ),
            ],
            any_order=True,
        )
        self.assertEqual(
            2,
            len(chat_mock.mock_calls),
            msg="The chat function should have been called twice.",
        )

    def verify_summarization_results(self):
        for query in VerifyGraphQueries:
            self.verify_query_result(query)

    def verify_query_result(self, query):
        self.assertEqual(
            query.good_result,
            self.db.query(query)[0][0],
            msg="The database graph is not as expected.",
        )
