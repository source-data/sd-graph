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
            logger.warning(f"Found {len(matching_nodes)} matching node(s) when updating node with DOI")

        for node in matching_nodes:
            existing_doi = node["doi"]
            if existing_doi == doi:
                # correct DOI is already set
                continue

            if existing_doi:
                logger.info(f"Updating DOI of node {node.id} from \"{existing_doi}\" to \"{doi}\"")
            else:
                logger.info(f"Setting DOI of node {node.id} to \"{doi}\"")

            if not dry_run:
                result = self.db.update_node(node.id, {"doi": doi})

    def run(self, input_dir: str, dry_run=True):
        deposition_files = [f for f in Path(input_dir).glob("*.yml")]
        logger.info(f"{len(deposition_files)} file found in MECADOI deposition dir at {input_dir}.")

        if dry_run:
            logger.info(f"Doing a dry run, the database will not be changed.")

        with logging_redirect_tqdm():
            for deposition_file in tqdm(deposition_files):
                with open(deposition_file, "r") as f:
                    articles = safe_load(f)
                logger.info(f"{len(articles)} articles found in {deposition_file}")

                queries_to_execute = []
                for article in articles:
                    article_doi = article["doi"]
                    logger.info(f"processing {article_doi}")

                    review_process = article["review_process"]
                    if len(review_process) != 1:
                        logger.warning(f"review process doesn't have exactly one revision round")
                    revision_round = review_process[0]

                    author_reply = revision_round.get("author_reply", None)
                    if author_reply is not None:
                        queries_to_execute.append(
                            (FIND_RESPONSE(params={"related_article_doi": article_doi}), author_reply["doi"])
                        )

                    for review_idx, review in enumerate(revision_round["reviews"], start=1):
                        query = FIND_REVIEW(params={"related_article_doi": article_doi, "review_idx": str(review_idx)})
                        queries_to_execute.append((query, review["doi"]))

                for query, doi in queries_to_execute:
                    self.update_node_with_doi(query, doi, dry_run=dry_run)


def main():
    parser = ArgumentParser(description="Load peer reviews from MECADOI deposition files.")
    parser.add_argument("--input-dir", help="The directory containing the MECADOI deposition files.")
    parser.add_argument(
        "--non-dry-run",
        action='store_true',
        help="Actually update the database instead of just outputting what would be changed."
    )
    args = parser.parse_args()
    input_dir = args.input_dir
    dry_run = not args.non_dry_run
    MecadoiImporter(DB).run(input_dir, dry_run=dry_run)


if __name__ == "__main__":
    common.logging.configure_logging()
    main()
