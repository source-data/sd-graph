from argparse import ArgumentParser
from requests import get
from tqdm import tqdm, trange
from tqdm.contrib.logging import logging_redirect_tqdm
import common.logging
from . import EEB_INTERNAL_API

logger = common.logging.get_logger(__name__)


def get_json(base_url, path):
    url = f"{base_url}{path}"
    response = get(url)
    response.raise_for_status()
    return response.json()


def get_paper_ids(papers):
    return [
        {"doi": paper["doi"], "slug": paper["slug"]}
        for paper in papers["items"]
    ]


def warmup_individual_method(base_url, get_path, params, no_progress):
    logger.info(f"Warming up cache for {get_path('{param}')} with {len(params)} params.")
    with logging_redirect_tqdm():
        for param in tqdm(params, disable=no_progress):
            path = get_path(param)
            get_json(base_url, path)


def warmup_paged_method(base_url, path_first_page, no_progress):
    response = get_json(base_url, path_first_page)
    yield get_paper_ids(response)
    n_pages = response["paging"]["totalPages"]

    with logging_redirect_tqdm():
        for page in trange(2, n_pages + 1, disable=no_progress):
            path_next_page = response["paging"]["next"]
            if not path_next_page:
                logger.error(f"Expected {n_pages} pages, but only got {page - 1}")
            response = get_json(base_url, path_next_page)
            yield get_paper_ids(response)
        if response["paging"]["next"]:
            logger.error(f"Expected {n_pages} pages, but got more.")


def cache_warm_up(base_url, no_progress=False):
    logger.info(f"Warming up cache using base URL {base_url}")

    # warm up the reviewing_services method
    path_reviewing_services = "/api/v2/reviewing_services/"
    logger.info("warming up %s", path_reviewing_services)
    reviewing_services = get_json(base_url, path_reviewing_services)

    paths_reviewing_services = [
        f"/api/v2/papers/?reviewedBy={rs['id']}"
        for rs in reviewing_services
    ]
    path_papers = "/api/v2/papers/"
    for path_reviewing_service in paths_reviewing_services:
        logger.info("warming up %s", path_reviewing_service)
        warmup_paged_method(base_url, path_papers, no_progress)

    logger.info("warming up %s", path_papers)
    paper_ids = [
        pid
        for pids in warmup_paged_method(base_url, path_papers, no_progress)
        for pid in pids
    ]

    logger.info("warming up /api/v2/paper/ for slugs and DOIs")
    slugs = set([pid["slug"] for pid in paper_ids])
    dois = set([pid["doi"] for pid in paper_ids])
    warmup_individual_method(base_url, lambda slug: f"/api/v2/paper/?slug={slug}", slugs, no_progress)
    warmup_individual_method(base_url, lambda doi: f"/api/v2/paper/?doi={doi}", dois, no_progress)

    logger.info("warming up /api/v2/docmap/{doi}")
    warmup_individual_method(base_url, lambda doi: f"/api/v2/docmap/{doi}", dois, no_progress)


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('base_url', default=EEB_INTERNAL_API,help='Host address to be warmed up')
    parser.add_argument('--no-progress', action='store_true', help='Do not output progress bars')
    args = parser.parse_args()
    cache_warm_up(args.base_url, no_progress=args.no_progress)
