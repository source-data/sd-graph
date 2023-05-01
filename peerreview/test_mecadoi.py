from pathlib import Path
from yaml import dump

import peerreview.mecadoi
from tests.utils import DbTestCase


class MecadoiImportTestCase(DbTestCase):
    input_dir = "/app/mecadoi"

    def test_dois_are_imported(self):
        self.load_db_fixtures(
            [
                """
            CREATE (a1:Article {doi: "10.1234/567890"})
            CREATE (a1)-[:HasReview]->(:Review {
                related_article_doi: a1.doi,
                reviewed_by: "review commons",
                review_idx: "1"
            })
            CREATE (a1)-[:HasReview]->(:Review {
                related_article_doi: a1.doi,
                reviewed_by: "review commons",
                review_idx: "2"
            })
            """
            ]
        )
        self.load_mecadoi_data(
            [
                {
                    "doi": "10.1234/567890",
                    "review_process": [
                        {
                            "reviews": [
                                {
                                    "doi": "10.1234/567890-review-1",
                                    "review_idx": "1",
                                },
                                {
                                    "doi": "10.1234/567890-review-2",
                                    "review_idx": "2",
                                },
                            ]
                        }
                    ],
                }
            ]
        )
        expected_database_state = [
            """
            MATCH (a1:Article {doi: "10.1234/567890"})
            MATCH (a1)-[:HasReview]->(:Review {
                doi: "10.1234/567890-review-1",
                related_article_doi: a1.doi,
                reviewed_by: "review commons",
                review_idx: "1"
            })
            MATCH (a1)-[:HasReview]->(:Review {
                doi: "10.1234/567890-review-2",
                related_article_doi: a1.doi,
                reviewed_by: "review commons",
                review_idx: "2"
            })
            RETURN
                CASE WHEN COUNT(*) = 1
                    THEN $good_result
                    ELSE "Failed: " + $good_result
                END AS result
            """
        ]

        self.run_import()
        self.verify_database_state(expected_database_state)

    def verify_database_state(self, expected_database_state):
        with self.db._driver.session() as session:
            for query in expected_database_state:
                good_result = "Good"
                self.assertEqual(
                    good_result,
                    session.write_transaction(
                        self.db._tx_funct, query, params={"good_result": good_result}
                    )[0][0],
                    msg=f"The database graph is not as expected for query {query}",
                )

    def load_db_fixtures(self, fixtures):
        with self.db._driver.session() as session:
            for fixture in fixtures:
                session.write_transaction(self.db._tx_funct, fixture)

    def load_mecadoi_data(self, data):
        with open(f"{self.input_dir}/test.yml", "w") as f:
            dump(data, f)

    def run_import(self, dry_run=False):
        peerreview.mecadoi.MecadoiImporter(peerreview.mecadoi.DB).run(
            self.input_dir, dry_run=dry_run
        )

    def setUp(self):
        input_path = Path(self.input_dir)
        input_path.mkdir(parents=True, exist_ok=True)
        num_input_files = len(list(input_path.glob("*")))
        self.assertEqual(
            0, num_input_files, msg=f"Input directory {self.input_dir} is not empty"
        )
        return super().setUp()

    def tearDown(self):
        for file in Path(self.input_dir).glob("*"):
            file.unlink()
        return super().tearDown()
