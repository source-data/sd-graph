import json
from argparse import ArgumentParser
import requests
from . import EEB_PUBLIC_API
from neotools.utils import progress


def cache_warm_up(base_url):

    print(f"waming up cache using {base_url}:")
    dois = []
    # warm up the stats method
    url = base_url + 'stats'
    r = requests.get(url, verify=False)
    print(f"method /stats warmed up: {r.status_code == 200}")
    for method in ['by_reviewing_service/', 'automagic/', 'by_auto_topics/']:
        url = base_url + method
        # warm up of the main methods
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            collections = None
            try:
                collections = response.json()
            except json.decoder.JSONDecodeError:
                print(f"response.content")
                raise
            N_collections = len(collections)
            for i, collection in enumerate(collections):
                papers = collection['papers']
                new_dois = [paper['doi'] for paper in papers]
                progress(i, N_collections, f"{method}{collection['id']} {len(new_dois)} dois              ")
                # warm up of the multiple doi method
                multi_dois_url = base_url + "dois/"
                r = requests.post(multi_dois_url, json={'dois': new_dois}, verify=False)
                if r.status_code == 200:
                    dois += new_dois
                else:
                    print(f"Problem with {method}{collection['id']}! Status code: {r.status_code}")
    dois = set(dois)  # remove duplicates
    N_dois = len(dois)
    print(f"\nfetched {N_dois} unique dois.")
    successes = 0
    for i, doi in enumerate(dois):
        progress(i, N_dois, f"{doi}                       ")
        # warm up of the individual doi method
        doi_url = base_url + "doi/{doi}"
        r = requests.get(doi_url, verify=False)
        successes += 1 if r.status_code == 200 else 0
    print(f"\ncache warmed up with {successes} out of {N_dois} dois.\n")


if __name__ == '__main__':
    parser = ArgumentParser(description='Loading meca or CORD-19 archives into neo4j.')
    parser.add_argument('base_url', default=EEB_PUBLIC_API,help='Host address to be warmed up')
    args = parser.parse_args()
    cache_warm_up(args.base_url)
