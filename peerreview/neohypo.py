import re
from typing import Dict, List
from . import HYPO, DB
from .queries import LINK_REVIEWS, LINK_RESPONSES, LINK_ANNOT

GROUP_IDS = {
    'NEGQVabn': 'review commons',
    'q5X6RWJ6': 'elife',
    'jKiXiKya': 'embo press',
}

REVIEWER_REGEX = re.compile(r'^.{,300}(referee|reviewer)\W+(\d)', re.IGNORECASE | re.DOTALL)
RESPONSE_REGEX = re.compile(r'^.{,300}Reply to the reviewers', re.IGNORECASE | re.DOTALL)


def type_of_annotation(hypo_row):
    text = hypo_row['text']
    if REVIEWER_REGEX.match(text):
        type = 'review'
    elif RESPONSE_REGEX.match(text):
        type = 'response'
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
        r = re.search(r'\n\n#### Significance\n\n(.*)', text, re.IGNORECASE | re.DOTALL)
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


class Hypothelink:

    def __init__(self, db, hypo):
        self.neo4j = db
        self.hypo = hypo

    def run(self, group_ids):
        for group_id in group_ids:
            hypo_rows = self.get_annot_from_hypo(group_id)
            for i, row in enumerate(hypo_rows):
                peer_review_node = self.hypo2node(row)
                peer_review_node.update_properties({'reviewed_by': GROUP_IDS[group_id]})
                peer_review_neo = self.neo4j.node(peer_review_node, clause="MERGE")
                print(f"loaded {peer_review_node.label} for {peer_review_node.properties['related_article_doi']}")
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
            response = self.hypo.annotations.search(group=group_id, limit=limit, offset=offset) # NEEDS PAGINATION USING
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

    def make_relationships(self):
        N_rev = self.neo4j.query(LINK_REVIEWS)
        N_resp = self.neo4j.query(LINK_RESPONSES)
        N_annot = self.neo4j.query(LINK_ANNOT)
        print(f"{N_rev}, {N_resp}, {N_annot}")


def main():

    Hypothelink(DB, HYPO).run(GROUP_IDS)


if __name__ == "__main__":
    main()
