import json
from argparse import ArgumentParser
from datetime import datetime
import requests
from tqdm import tqdm, trange
from tqdm.contrib.logging import logging_redirect_tqdm
import common.logging
from . import EEB_INTERNAL_API

logger = common.logging.get_logger(__name__)

def cache_warm_up(base_url, no_progress=False):
    logger.info(f"Warming up cache using base URL {base_url}")
    dois = []
    slugs = []
    # warm up the stats method
    url = base_url + '/v1/stats'
    r = requests.get(url)
    logger.info(f"Method /stats warmed up: {r.status_code == 200}")
    for method in ['by_reviewing_service/', 'automagic/', 'by_auto_topics/']:
        logger.info(f'Warming up collections for method "{method}"')
        url = base_url + '/v1/' + method
        # warm up of the main methods
        response = requests.get(url)
        if response.status_code == 200:
            collections = None
            try:
                collections = response.json()
            except json.decoder.JSONDecodeError:
                logger.error(f"content: {response.content}")
                raise
            N_collections = len(collections)
            with logging_redirect_tqdm():
                for collection in tqdm(collections, disable=no_progress):
                    papers = collection['papers']
                    new_dois = [paper['doi'] for paper in papers]
                    logger.info(f'  Warming up collection \"{collection["id"]}\" with {len(new_dois)} DOIs')
                    # warm up of the multiple doi method
                    multi_dois_url = base_url + "/v1/dois/"
                    r = requests.post(multi_dois_url, json={'dois': new_dois})
                    if r.status_code == 200:
                        dois += new_dois
                        slugs += [paper['slug'] for paper in papers]
                    else:
                        logger.warning(f"  Failed to warm up collection \"{collection['id']}\" of method \"{method}\"! Status code: {r.status_code}, message: {r.text}")
        else:
            logger.warning(f"Failed to fetch collections of method \"{method}\"! Status code: {response.status_code}, message: {response.text}")

    # remove duplicates
    dois = set(dois)
    slugs = set(slugs)

    N_dois = len(dois)
    N_slugs = len(slugs)
    logger.info(f"fetched {N_dois} unique dois, {N_slugs} unique slugs.")

    num_slug_successes = warmup_individual_method(lambda slug: f"{base_url}/v1/slug/{slug}", slugs, no_progress)
    logger.info(f"cache warmed up with {num_slug_successes} out of {N_slugs} slugs.")

    num_docmap_successes = warmup_individual_method(lambda doi: f"{base_url}/v2/docmap/{doi}", dois, no_progress)
    logger.info(f"cache warmed up with {num_docmap_successes} out of {N_dois} DOIs.")


def warmup_individual_method(get_url, params, no_progress):
    successes = 0
    logger.info(f"Warming up cache for {get_url('{param}')} with {len(params)} params.")
    with logging_redirect_tqdm():
        for param in tqdm(params, disable=no_progress):
            url = get_url(param)
            r = requests.get(url)
            if r.status_code == 200:
                successes += 1
            else:
                logger.warning(f"Failed to warm up cache for {url}! Status code: {r.status_code}, message: {r.text}")
    return successes


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('base_url', default=EEB_INTERNAL_API,help='Host address to be warmed up')
    parser.add_argument('--no-progress', action='store_true', help='Do not output progress bars')
    args = parser.parse_args()
    cache_warm_up(args.base_url, no_progress=args.no_progress)
