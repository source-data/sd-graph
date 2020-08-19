import re
from argparse import ArgumentParser
from typing import Dict
from neotools.utils import progress
from . import HYPO, DB
from .queries import (
    NotYetPublished, UpdatePublicationStatus,
    MATCH_DOI, LINK_REVIEWS, LINK_RESPONSES, LINK_ANNOT
)
from sdg.sdnode import API
from neotools.txt2node import JSONNode
from neotools.rxiv2neo import build_neo_graph
from neotools.model import CROSSREF_PREPRINT_API_GRAPH_MODEL

GROUP_IDS = {
    'NEGQVabn': 'review commons',
    'q5X6RWJ6': 'elife',
    'jKiXiKya': 'embo press',
    '9Nn8DMax': 'peerage of science',
}

REVIEWER_REGEX = re.compile(r'^.{,300}(referee|reviewer)\W+(\d)', re.IGNORECASE | re.DOTALL)
RESPONSE_REGEX = re.compile(r'^.{,100}This rebuttal was posted by the corresponding author to \*Review Commons\*', re.IGNORECASE | re.DOTALL)


def type_of_annotation(hypo_row):
    text = hypo_row['text']
    if RESPONSE_REGEX.match(text):  # this pattern first, since 'reviewer' will appear in response as well
        type = 'response'
    elif REVIEWER_REGEX.match(text):
        type = 'review'
    else:
        type = 'undetermined'
    return type


def doi_from_uri(uri):
    # dirty for now: strip away the version postfix from the biorixv uri
    # 'https://www.biorxiv.org/content/10.1101/733097v2'
    doi = re.search(r'10\.1101/[\d\.]+', uri).group(0)
    return doi


class PeerReviewNode:
    def __init__(self, hypo_row):
        self._resp = hypo_row
        self.label = 'PeerReviewMaterial'
        self.properties = {}
        self.update_properties({
            'posting_date': self.posting_date,
            'text': self.text,
            'related_article_uri': self.related_article,
            'related_article_doi': self.related_doi,
        })

    def update_properties(self, prop: Dict):
        self.properties = {**self.properties, **prop}

    @property
    def posting_date(self):
        return self._resp['created']

    @property
    def text(self):
        return self._resp['text']

    @property
    def related_article(self):
        return self._resp['uri']

    @property
    def related_doi(self):
        return doi_from_uri(self.related_article)


class ReviewCommonsReviewNode(PeerReviewNode):
    def __init__(self, hypo_row):
        super().__init__(hypo_row)
        self.label = 'Review'
        self.update_properties({
            'review_idx': self.reviewer_idx,
            'highlight': self.significance_section
        })

    @property
    def significance_section(self):
        text = self._resp['text']
        r = re.search(r'\n\n#### Significance\w*\n\n(.*)', text, re.IGNORECASE | re.DOTALL)
        if r:
            section = r.group(1)
        else:
            section = ''
        return section

    @property
    def reviewer_idx(self):
        # ### Referee \\#2\n\n
        # ###Reviewer #3\n\n
        body = self._resp['text']
        reviewer = REVIEWER_REGEX.match(body)
        if reviewer:
            reviewer_idx = reviewer.group(2)
        else:
            reviewer_idx = None
        return reviewer_idx


class ReviewCommonsResponseNode(PeerReviewNode):
    def __init__(self, hypo_row):
        super().__init__(hypo_row)
        self.label = 'Response'


class BioRxiv(API):
    def __init__(self):
        super().__init__()

    def details(self, doi: str) -> Dict:
        url = f'https://api.biorxiv.org/detail/{doi}'
        response = self.rest2data(url)
        # TODO: test if response not empty first
        if response['messages'][0]['status'] == 'ok':
            response = response['collection'][0]
        else:
            response = {} 
        return response


class CrossRef(API):
    def __init__(self):
        super().__init__()

    def details(self, doi: str) -> Dict:
        url = f'https://doi.org/{doi}'
        response = self.rest2data(url)
        return response


class Hypothelink:

    def __init__(self, db, hypo):
        self.db = db
        self.hypo = hypo
        self.biorxiv = BioRxiv()
        self.crossref = CrossRef()

    def run(self, group_ids):
        for group_id in group_ids:
            hypo_rows = self.get_annot_from_hypo(group_id)
            for row in hypo_rows:
                peer_review_node = self.hypo2node(row)
                peer_review_node.update_properties({'reviewed_by': GROUP_IDS[group_id]})
                peer_review_neo = self.db.node(peer_review_node, clause="MERGE")
                print(f"loaded {peer_review_node.label} for {peer_review_node.properties['related_article_doi']}")
                # check if article node missing and add temporary one with source='biorxiv_crossref'
                self.add_prelim_article(peer_review_node)
        self.make_relationships()

    @staticmethod
    def hypo2node(hypo_row):
        annot_type = type_of_annotation(hypo_row)
        if annot_type == 'review':
            return ReviewCommonsReviewNode(hypo_row)
        elif annot_type == 'response':
            return ReviewCommonsResponseNode(hypo_row)
        else:
            return PeerReviewNode(hypo_row)

    def get_annot_from_hypo(self, group_id: str):
        # https://api.hypothes.is/api/search?group=NEGQVabn
        rows = []
        limit = 200
        offset = 0
        remaining = 1
        while remaining > 0:
            response = self.hypo.annotations.search(group=group_id, limit=limit, offset=offset)
            if response.status_code == 200:
                response = response.json()
                N = response['total']  # does not change
                remaining = N - offset
                offset += limit
                print(f"found {N} annotations for group {GROUP_IDS[group_id]}")
                rows += response['rows']
            else:
                print(f"PROBLEM: {response.status_code}")
                rows = None
                remaining = 0
        return rows

    def add_prelim_article(self, peer_review_node: PeerReviewNode):
        # exists?
        doi = peer_review_node.related_doi
        q = MATCH_DOI(params={'doi': doi})
        if not self.db.exists(q):
            # fetch metadata from bioRxiv and CrossRef
            data_biorxiv = self.biorxiv.details(doi)
            data = self.crossref.details(doi)
            if data and data_biorxiv:
                data['abstract'] = data_biorxiv['abstract']  # abstract in bioRxiv is plain text while CrossRef has jats namespaced formatting tags
                prelim = JSONNode(data, CROSSREF_PREPRINT_API_GRAPH_MODEL)
                prelim.properties['version'] = data_biorxiv['version']
                # add nodes to database
                build_neo_graph(prelim, 'biorxiv_crossref', self.db)
            else:
                print(f"problem with doi={doi}")

    def make_relationships(self):
        N_rev = self.db.query(LINK_REVIEWS())
        N_resp = self.db.query(LINK_RESPONSES())
        N_annot = self.db.query(LINK_ANNOT())
        print(f"{N_rev}, {N_resp}, {N_annot}")


def main():
    Hypothelink(DB, HYPO).run(GROUP_IDS)


if __name__ == "__main__":
    main()
