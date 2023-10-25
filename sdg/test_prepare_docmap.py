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

    def __init__(self, doi, journal_title, publication_date, has_review, has_peer_review_material):
        params = {
            "doi": doi,
            "journal_title": journal_title,
            "publication_date": publication_date,
            "title": f"Article {doi}",
        }
        self.code = """
        CREATE (a:Article {
            doi: $doi,
            journal_title: $journal_title,
            publication_date: $publication_date,
            title: $title
        })
        """
        if has_review:
            self.code += """
            CREATE (a)-[:HasReview]->(:Review { reviewed_by: $reviewed_by })
            """
        if has_peer_review_material:
            self.code += """
            CREATE (a)-[:HasAnnot]->(:PeerReviewMaterial { reviewed_by: $reviewed_by })
            """
        if has_review or has_peer_review_material:
            params["reviewed_by"] = CreateReviewService.name

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

class DocmapTestCase(DbTestCase):

    def setUp(self):
        super().setUp()
        self.db.query(CreateReviewService())

    def run_prepare_docmap(self):
        run_flow(self.db, PrepareDocmapTasks, "test_prepare_docmap")

    def test_docmaps_are_created(self):
        article_fixtures = [
            # article_args, docmap_present
            (["10.1234/01", "bioRxiv", "2020-01-01", False, False], False),  # no review and no peer review material => no docmap
            (["10.1234/02", "bioRxiv", "2020-01-01", True,  False], True),   # review but no peer review material    => docmap
            (["10.1234/03", "bioRxiv", "2020-01-01", False, True],  True),   # no review but peer review material    => docmap
            (["10.1234/04", "bioRxiv", "2020-01-01", True,  True],  True),   # both review and peer review material  => docmap
        ]
        for args, _ in article_fixtures:
            self.db.query(CreateArticle(*args))
        
        self.run_prepare_docmap()

        for args, docmap_present in article_fixtures:
            doi, _, publication_date = args[:3]
            verify_query = VerifyDocmapPresent(doi, publication_date, docmap_present)
            self.assertEqual(
                verify_query.good_result,
                self.db.query(verify_query)[0][0],
                msg="The database graph is not as expected.",
            )


