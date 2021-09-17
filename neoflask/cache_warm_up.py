import json
from argparse import ArgumentParser
import requests
from tqdm import tqdm
import common.logging
from . import EEB_PUBLIC_API

logger = common.logging.get_logger(__name__)

def cache_warm_up(base_url):

    logger.info(f"waming up cache using {base_url}:")
    dois = []
    # warm up the stats method
    url = base_url + 'stats'
    r = requests.get(url, verify=False)
    logger.info(f"method /stats warmed up: {r.status_code == 200}")
    for method in ['by_reviewing_service/', 'automagic/', 'by_auto_topics/']:
        url = base_url + method
        # warm up of the main methods
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            collections = None
            try:
                collections = response.json()
            except json.decoder.JSONDecodeError:
                logger.info(f"content: {response.content}")
                raise
            N_collections = len(collections)
            for collection in tqdm(collections):
                papers = collection['papers']
                new_dois = [paper['doi'] for paper in papers]
                # warm up of the multiple doi method
                multi_dois_url = base_url + "dois/"
                r = requests.post(multi_dois_url, json={'dois': new_dois}, verify=False)
                if r.status_code == 200:
                    dois += new_dois
                else:
                    logger.warning(f"Problem with {method}{collection['id']}! Status code: {r.status_code}")
    dois = set(dois)  # remove duplicates
    N_dois = len(dois)
    logger.info(f"\nfetched {N_dois} unique dois.")
    successes = 0
    for doi in tqdm(dois):
        # warm up of the individual doi method
        doi_url = base_url + "doi/{doi}"
        r = requests.get(doi_url, verify=False)
        successes += 1 if r.status_code == 200 else 0
    logger.info(f"\ncache warmed up with {successes} out of {N_dois} dois.\n")


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('base_url', default=EEB_PUBLIC_API,help='Host address to be warmed up')
    args = parser.parse_args()
    cache_warm_up(args.base_url)
