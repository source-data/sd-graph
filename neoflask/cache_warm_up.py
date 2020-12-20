import requests
from . import EEB_PUBLIC_API
from neotools.utils import progress


def cache_warm_up(base_url):

    def get_all_dois():
        
        return dois

    print(f"waming up cache using {EEB_PUBLIC_API}:")
    dois = []
    # warm up ths stats method
    url = base_url + 'stats'
    r = requests.get(url)
    print(f"method /stats warmed up: {r.status_code == 200}")
    for method in ['by_reviewing_service/', 'automagic/', 'by_auto_topics/']:
        url = base_url + method
        # warm up of the main methods
        r = requests.get(url)
        if r.status_code == 200:
            collections = r.json()
            N_collections = len(collections)
            for i, collection in enumerate(collections):
                progress(i, N_collections, f"{collection['id']}")
                papers = collection['papers']
                new_dois = [paper['doi'] for paper in papers]
                # warm up of the multiple doi method
                multi_dois_url = EEB_PUBLIC_API + "dois/"
                r = requests.post(multi_dois_url, json={'dois': new_dois})
                if r.status_code == 200:
                    dois += new_dois
    dois = set(dois)  # remove duplicates
    N_dois = len(dois)
    print(f"\nfetched {N_dois} unique dois.")
    successes = 0
    for i, doi in enumerate(dois):
        progress(i, N_dois, f"{doi}")
        # warm up of the individual doi method
        doi_url = EEB_PUBLIC_API + "doi/{doi}"
        r = requests.get(doi_url)
        successes += 1 if r.status_code == 200 else 0
    print(f"\ncache warmed up with {successes} out of {N_dois} dois.")


def main():
    cache_warm_up(EEB_PUBLIC_API)


if __name__ == '__main__':
    main()
