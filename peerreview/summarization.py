"""Summarize peer reviews from MECADOI deposition files."""

from argparse import ArgumentParser
from json import dumps
from re import IGNORECASE, search, sub
from string import Template
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import common.logging
from . import DB
from .gpt import chat, review_summarization_parameters, review_summarization_prompt
from .queries import (
    CREATE_SUMMARY,
    MERGE_SUMMARIZATION_CONFIG,
    REVIEWS_WITHOUT_SUMMARIES,
)

logger = common.logging.get_logger(__name__)


def _filter_significance_sections(significance_sections):
    """
    Filters boilerplate from the significance section of the given reviews.

    Returns None if the review is too short (< 25 chars) and the filtered text of
    the significance section otherwise.

    Filtered out are:
    - Referee cross-commenting and everything that follows.
    - Any "Significance" subheadings that are in the text.
    - Any Markdown around subheadings (i.e. **Heading** -> Heading)
    """
    filtered_significance_sections = []
    for significance_section in significance_sections:
        text = significance_section
        start_of_cross_commenting = search(
            r"\*\*.*?cross-comment", text, flags=IGNORECASE
        )
        if start_of_cross_commenting:
            text = text[: start_of_cross_commenting.start()]

        text = sub(r"\*\*significance:?\*\*", "", text, flags=IGNORECASE)
        text = sub(r"####\s*significance:?", "", text, flags=IGNORECASE)
        text = sub(r"\*{1,4}(.+?)\*{1,4}", r"\1", text)
        text = text.strip()

        if len(text) < 25:
            continue

        filtered_significance_sections.append(text)

    return filtered_significance_sections


def _generate_summary(significance_sections, dry_run=True):
    filtered_significance_sections = _filter_significance_sections(
        significance_sections
    )

    review_template = Template("Review #$review_number:\n$review")
    review_seperator = "\n\n"
    reviews_text = review_seperator.join(
        [
            review_template.substitute(review_number=i, review=review)
            for i, review in enumerate(filtered_significance_sections, start=1)
        ]
    )
    prompt = review_summarization_prompt(reviews_text)
    logger.debug("Prompt for chat:\n%s", prompt)
    summary = chat(prompt, review_summarization_parameters, dry_run=dry_run)
    return reviews_text, summary


def _get_significance_sections(summarizable_reviews):
    """Returns the significance sections of the given reviews.

    Accepts a dict mapping article DOIs to lists of reviews, and returns a dict mapping
    article DOIs to lists of significance sections.
    If no significance section can be found for a review, the article and its
    reviews are not included in the returned dict.
    """
    sig_sections_by_article_doi = {}
    for article_doi, reviews in summarizable_reviews.items():
        significance_sections = []
        reviews_without_sig_section = []
        for review in reviews:
            significance_section = review.get("text_significance", None)

            if significance_section is None:
                reviews_without_sig_section.append(review)
                continue

            significance_sections.append(significance_section)

        if len(reviews_without_sig_section) > 0:
            logger.warning(
                "Found %d/%d reviews without significance section for article %s",
                len(reviews_without_sig_section),
                len(reviews),
                article_doi,
            )
        else:
            sig_sections_by_article_doi[article_doi] = significance_sections

    return sig_sections_by_article_doi


class Summarizer:
    """Entrypoint for summarizing peer reviews.

    After running this script, the database will contain a new :Summary node for each
    summary, which will be connected 1) through a :HasSummary relationship to the set
    of reviews it summarizes and 2) through a :GeneratedWith relationship to the
    parameters and prompt template used for generating the summary.
    """

    def __init__(self, db):
        self.db = db

    def run(self, dry_run=True):
        """Summarize all not-yet-summarized peer reviews in the database.

        This method...
        1) Grabs all not-yet-summarized but summarizable peer reviews from the database.
        We are summarizing only the significance sections of the reviews so far, and
        these are only present for reviews from Review Commons (that's the summarizable
        part).

        2) for each set of reviews, it tries to grab the significance sections from the
        review texts. If these can't be found the reviews are skipped.

        3) for each set of significance sections, it tries to generate a summary using
        OpenAI's GPT-3.5 API and stores it in the database as a new node (after this
        step the set of reviews will no longer be considered "not-yet-summarized" and
        will not be returned during step 1 in future calls of this method).
        """
        if dry_run:
            logger.info("Doing a dry run, the database will not be changed.")

        summarizable_reviews = self.get_summarizable_reviews()
        logger.info(
            "Found %d articles with reviews that aren't summarized",
            len(summarizable_reviews),
        )
        significance_sections = _get_significance_sections(summarizable_reviews)
        logger.info(
            "Found %d articles with significance sections in all reviews",
            len(significance_sections.keys()),
        )

        summarization_config = self.get_summarization_config(dry_run=dry_run)
        logger.info("Summarizing reviews with this config: %s", summarization_config)

        max_total_failure_count = 10
        failure_count = 0
        with logging_redirect_tqdm():
            for (
                article_doi,
                significance_sections,
            ) in tqdm(significance_sections.items()):
                reviews_text, summary = None, None
                try:
                    reviews_text, summary = _generate_summary(
                        significance_sections, dry_run=dry_run
                    )
                except Exception:
                    logger.error(
                        "Failed to generate summary for reviews of article %s.",
                        article_doi,
                        exc_info=True,
                    )
                    failure_count += 1
                    if failure_count > max_total_failure_count:
                        logger.error("Aborting summary generation, too many failures")
                        break
                    continue

                if summary is not None:
                    logger.debug(
                        'Setting summary of reviews of article %s to "%s"',
                        article_doi,
                        summary,
                    )
                    self._update_with_summary(
                        article_doi,
                        reviews_text,
                        summary,
                        summarization_config,
                        dry_run=dry_run,
                    )

    def get_summarization_config(self, dry_run=True):
        summarization_params = {
            "parameters": dumps(
                review_summarization_parameters, indent=4, sort_keys=True
            ),
            "prompt": dumps(
                review_summarization_prompt("$reviews_text"), indent=4, sort_keys=True
            ),
        }
        if dry_run:
            summarization_config = dict({"id": 0}, **summarization_params)
        else:
            summarization_config = self.db.query(
                MERGE_SUMMARIZATION_CONFIG(params=summarization_params)
            )[0][0]
        return summarization_config

    def get_summarizable_reviews(self):
        """Returns all reviews from the database that can be summarized.

        Grabs all Review Commons reviews that don't have a summary yet. Only for Review
        Commons reviews we can get the significance sections needed to summarize from
        the MECADOI deposition files.

        This function returns a dict with article DOIs as keys and, as values, a list of
        the article's reviews. The reviews are sorted by the index of the review in the
        article's set of reviews.
        """
        data = [
            r.data()
            for r in self.db.query(
                REVIEWS_WITHOUT_SUMMARIES(params={"reviewed_by": "review commons"})
            )
        ]
        return {d["article_doi"]: d["reviews"] for d in data}

    def _update_with_summary(
        self,
        article_doi,
        reviews_text,
        summary_text,
        summarization_config,
        dry_run=True,
    ):
        if not dry_run:
            self.db.query(
                CREATE_SUMMARY(
                    params={
                        "article_doi": article_doi,
                        "reviews_text": reviews_text,
                        "summary_text": summary_text,
                        "id_summarization_config": summarization_config.id,
                    }
                )
            )


def main():
    parser = ArgumentParser(
        description=(
            """Generate summaries of peer reviews from their significance sections.

By default this command only outputs what would happen.
Pass --no-dry-run to actually update the database."""
        )
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help=(
            "Actually update the database instead of just outputting what would be"
            " changed."
        ),
    )
    args = parser.parse_args()
    dry_run = not args.no_dry_run
    Summarizer(DB).run(dry_run=dry_run)


if __name__ == "__main__":
    common.logging.configure_logging()
    main()
