import json
from argparse import ArgumentParser
import requests
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import common.logging
from . import EEB_PUBLIC_API

logger = common.logging.get_logger(__name__)

def cache_warm_up(base_url):

    logger.info(f"Warming up cache using base URL {base_url}")
    dois = []
    # warm up the stats method
    url = base_url + 'stats'
    r = requests.get(url)
    logger.info(f"Method /stats warmed up: {r.status_code == 200}")
    for method in ['by_reviewing_service/', 'automagic/', 'by_auto_topics/']:
        logger.info(f'Warming up collections for method "{method}"')
        url = base_url + method
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
                for collection in tqdm(collections):
                    papers = collection['papers']
                    new_dois = [paper['doi'] for paper in papers]
                    logger.info(f'  Warming up collection \"{collection["id"]}\" with {len(new_dois)} DOIs')
                    # warm up of the multiple doi method
                    multi_dois_url = base_url + "dois/"
                    r = requests.post(multi_dois_url, json={'dois': new_dois})
                    if r.status_code == 200:
                        dois += new_dois
                    else:
                        logger.warning(f"  Failed to warm up collection \"{collection['id']}\" of method \"{method}\"! Status code: {r.status_code}, message: {r.text}")
        else:
            logger.warning(f"Failed to fetch collections of method \"{method}\"! Status code: {response.status_code}, message: {response.text}")
    dois = set(dois)  # remove duplicates
    N_dois = len(dois)
    logger.info(f"fetched {N_dois} unique dois.")
    successes = 0
    with logging_redirect_tqdm():
        for doi in tqdm(dois):
            # warm up of the individual doi method
            doi_url = base_url + "doi/{doi}"
            r = requests.get(doi_url)
            successes += 1 if r.status_code == 200 else 0
    logger.info(f"cache warmed up with {successes} out of {N_dois} dois.")


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('base_url', default=EEB_PUBLIC_API,help='Host address to be warmed up')
    args = parser.parse_args()
    cache_warm_up(args.base_url)
