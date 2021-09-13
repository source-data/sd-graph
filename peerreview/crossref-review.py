import re
import math
from argparse import ArgumentParser
from typing import Dict
from tqdm import trange
import common.logging
from neotools.utils import progress
from . import DB
from .queries import (
    NotYetPublished, UpdatePublicationStatus,
    MATCH_DOI, LINK_REVIEWS, LINK_RESPONSES, LINK_ANNOT
)
from sdg.sdnode import API
from neotools.txt2node import JSONNode
from neotools.rxiv2neo import build_neo_graph
from neotools.model import CROSSREF_PEERREVIEW_GRAPH_MODEL, CROSSREF_PCI_REVIEW_GRAPH_MODEL

logger = common.logging.get_logger(__name__)

"""
https://api.crossref.org/prefixes/10.24072/works?select
https://doi.org/10.24072/pci.ecology.100053


http://api.crossref.org/v1/works?filter=relation.type:is-review-of,relation.object:10.2139/ssrn.3640428

http://api.crossref.org/v1/works?filter=relation.type:is-review-of,relation.object:10.2139/ssrn.3640428
https://api.crossref.org/members/311/works?filter=type:peer-review
https://api.crossref.org/prefixes/{prefix}/works?filter=type:peer-review

get all reviews from prefix, extract set of is-review-of.doi

"""


# for RR:C19
class CrossRefPeerReview(API):
    def __init__(self):
        super().__init__()

    def details(self, prefix: str) -> Dict:
        url_summary = f'https://api.crossref.org/prefixes/{prefix}/works?filter=type:peer-review&rows=0'
        summary_results = self.rest2data(url_summary)
        if summary_results['status'] == 'ok':
            total_results = summary_results['message']['total-results']
            items_per_page = 1000
            offset = 0
            pages = math.ceil(total_results / items_per_page)
            items = []
            check = 0
            logger.info(f"total_results, items_per_page, pages:", total_results, items_per_page, pages)
            for offset in trange(0, items_per_page * pages, items_per_page):
                url = f'https://api.crossref.org/prefixes/{prefix}/works?filter=type:peer-review&rows={items_per_page}&offset={offset}'
                response = self.rest2data(url)
                new_items = response['message']['items']
                items += new_items
                check += len(new_items)
            assert check == total_results
        else:
            import pdb; pdb.set_trace()
        return items


# for PCI
class CrossRefWorks(API):
    def __init__(self):
        super().__init__()

    def details(self, prefix: str) -> Dict:
        url_summary = f'https://api.crossref.org/prefixes/{prefix}/works?rows=0'
        summary_results = self.rest2data(url_summary)
        if summary_results['status'] == 'ok':
            total_results = summary_results['message']['total-results']
            items_per_page = 1000
            offset = 0
            pages = math.ceil(total_results / items_per_page)
            items = []
            check = 0
            logger.info(f"total_results, items_per_page, pages:", total_results, items_per_page, pages)
            for offset in trange(0, items_per_page * pages, items_per_page):
                url = f'https://api.crossref.org/prefixes/{prefix}/works?rows={items_per_page}&offset={offset}'
                response = self.rest2data(url)
                new_items = response['message']['items']
                items += new_items
                check += len(new_items)
            assert check == total_results
        else:
            import pdb; pdb.set_trace()
        return items


def is_review_of(r, target_prefixes):
    peer_review_of = r.get('relation', {}).get('is-review-of', [])
    if peer_review_of:
        is_review_of_this_doi = peer_review_of[0]['id']
        reg = re.match(r'^(\d+\.\d+)/', is_review_of_this_doi)
        if reg:
            prefix = reg.group(1)
            if prefix in target_prefixes:
                return prefix
    return False


SOURCES = {
    'PCI': '10.24072',
    'RRC19': '10.1162',
}


class CrossRefReviewFinder:

    MODELS = {
        '10.1162': CROSSREF_PEERREVIEW_GRAPH_MODEL,
    }

    def __init__(self, db):
        self.db = db
        self.crossref = CrossRefPeerReview()

    def run(self, source_prefix, target_prefixes):
        items = self.crossref.details(source_prefix)
        for item in items:
            if is_review_of(item, target_prefixes):
                peer_review_node = JSONNode(item, self.MODELS[source_prefix])
                logger.info(peer_review_node)
                # rev_neo_node = self.db.node(peer_review_node, clause="MERGE")
                # self.add_prelim_article(peer_review_node)
         # self.make_relationships()


class PCIFinder:

    MODELS = {
        '10.24072': CROSSREF_PCI_REVIEW_GRAPH_MODEL,
    }

    def __init__(self, db):
        self.db = db
        self.crossref = CrossRefWorks()

    def run(self, source_prefix, target_prefixes):
        items = self.crossref.details(source_prefix)
        for item in items:
            if is_review_of(item, target_prefixes):
                # try:
                peer_review_node = JSONNode(item, self.MODELS[source_prefix])
                # except Exception as e:
                #     logger.info(e)
                #     import pdb; pdb.set_trace()
                logger.info(peer_review_node)
                # rev_neo_node = self.db.node(peer_review_node, clause="MERGE")
                # self.add_prelim_article(peer_review_node)
        # self.make_relationships()


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description="Upload peer review material using CrossRef.")
    parser.add_argument('-S', '--source', default='CCR19', help='Name of the reviewing service (source) to scan.')
    parser.add_argument('-T', '--targets', default=['10.1101'], help='DOI prefix of the published reviewed papers (target).')
    args = parser.parse_args()
    source = args.source
    target_prefixes = args.targets
    source_prefix = SOURCES[source]
    if source == 'PCI':
        PCIFinder(DB).run(source_prefix, target_prefixes)
    elif source == 'RRC19':
        PeerReviewFinder(DB).run(source_prefix, target_prefixes)
    else:
        logger.info("no model yet for this source")
