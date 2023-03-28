from argparse import ArgumentParser
from pathlib import Path
from neotools.queries import FIND_RESPONSE, FIND_REVIEW
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from yaml import safe_load
import common.logging
from . import DB

logger = common.logging.get_logger(__name__)


class MecadoiImporter:
    def __init__(self, db):
        self.db = db

    def update_node_with_doi(self, query, doi, dry_run=True):
        matching_nodes = [r["r"] for r in self.db.query(query)]

        if matching_nodes is None or len(matching_nodes) != 1:
            logger.warning(
                "Found %s matching node(s) when updating node with DOI %s",
                len(matching_nodes),
                doi,
            )

        for node in matching_nodes:
            existing_doi = node["doi"]
            if existing_doi == doi:
                # correct DOI is already set
                continue

            if existing_doi:
                logger.info(
                    'Updating DOI of node %s from "%s" to "%s"',
                    node.id,
                    existing_doi,
                    doi,
                )
            else:
                logger.info('Setting DOI of node %s to "%s"', node.id, doi)

            if not dry_run:
                self.db.update_node(node.id, {"doi": doi})

    def run(self, input_dir: str, dry_run=True):
        deposition_files = [f for f in Path(input_dir).glob("*.yml")]
        logger.info(
            "%s file found in MECADOI deposition dir at %s.",
            len(deposition_files),
            input_dir,
        )

        if dry_run:
            logger.info("Doing a dry run, the database will not be changed.")

        with logging_redirect_tqdm():
            for deposition_file in tqdm(deposition_files):
                with open(deposition_file, "r") as f:
                    articles = safe_load(f)
                logger.info("%s articles found in %s", len(articles), deposition_file)

                for article in articles:
                    article_doi = article["doi"]
                    logger.info("processing %s", article_doi)

                    review_process = article["review_process"]
                    if len(review_process) != 1:
                        logger.warning(
                            "review process doesn't have exactly one revision round"
                        )
                    revision_round = review_process[0]

                    queries_to_execute = []

                    author_reply = revision_round.get("author_reply", None)
                    if author_reply is not None:
                        queries_to_execute.append(
                            (
                                FIND_RESPONSE(
                                    params={"related_article_doi": article_doi}
                                ),
                                author_reply["doi"],
                            )
                        )

                    for default_review_idx, review in enumerate(
                        revision_round["reviews"], start=1
                    ):
                        review_idx = review.get("review_idx", default_review_idx)
                        query = FIND_REVIEW(
                            params={
                                "related_article_doi": article_doi,
                                "review_idx": str(review_idx),
                            }
                        )
                        queries_to_execute.append((query, review["doi"]))

                    for query, doi in queries_to_execute:
                        self.update_node_with_doi(query, doi, dry_run=dry_run)


def main():
    parser = ArgumentParser(
        description="""Load peer reviews from MECADOI deposition files.

By default this command only outputs what would happen.
Pass --no-dry-run to actually update the database."""
    )
    parser.add_argument(
        "--input-dir", help="The directory containing the MECADOI deposition files."
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help=(
            "Actually update the database instead of just"
            " outputting what would be changed."
        ),
    )
    args = parser.parse_args()
    input_dir = args.input_dir
    dry_run = not args.no_dry_run
    MecadoiImporter(DB).run(input_dir, dry_run=dry_run)


if __name__ == "__main__":
    common.logging.configure_logging()
    main()
