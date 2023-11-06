import re
import time
from random import randint
from string import Template
from argparse import ArgumentParser
from typing import Dict
import common.logging
from . import HYPO, DB
from .queries import (
    MATCH_DOI, LINK_REVIEWS, LINK_RESPONSES, LINK_ANNOT
)
from sdg.sdnode import API
from neotools.txt2node import JSONNode
from neotools.rxiv2neo import build_neo_graph
from neotools.model import (
    CROSSREF_PREPRINT_API_GRAPH_MODEL,
    CROSSREF_PEERREVIEW_GRAPH_MODEL,
    CROSSREF_PCI_REVIEW_GRAPH_MODEL
)

logger = common.logging.get_logger(__name__)

HYPO_GROUP_IDS = {
    'NEGQVabn': 'review commons',
    'q5X6RWJ6': 'elife',
    'jKiXiKya': 'embo press',
    '9Nn8DMax': 'peerage of science',
    'LN28Q33j': 'peer ref',
}


REVIEWER_REGEX = re.compile(r'^.{,300}(referee|reviewer)\W+(\d)', re.IGNORECASE | re.DOTALL)
RESPONSE_REGEX = re.compile(r'^.{,100}This (rebuttal|response) was posted by the corresponding author to \*Review Commons\*', re.IGNORECASE | re.DOTALL)


def type_of_annotation(hypo_row):
    text = hypo_row['text']
    tags = [t.lower() for t in hypo_row['tags']]  # for PeerRef
    if RESPONSE_REGEX.match(text) or 'discussion, revision and decision' in tags:  # this pattern first, since 'reviewer' will appear in response as well
        type = 'response'
    elif REVIEWER_REGEX.match(text) or 'review report' in tags:
        type = 'review'
    elif 'requires revisions' not in tags and 'under review' not in tags:  # excluding this kind of annotations from PeerRef
        type = 'peer review material'
    else:
        type = 'undetermined'
    return type


def doi_from_uri(uri):
    # how to do a uri-to-doi inverse lookup?
    # dirty for now: strip away the version postfix from the biorixv uri
    # 'https://www.biorxiv.org/content/10.1101/733097v2'
    doi = re.search(r'10\.1101/[\d\.]+', uri)
    if doi is not None:
        doi = doi.group(0)
    else:
        message = f"doi of related article could not be extracted from uri={uri}"
        logger.warning(message)
    return doi


class PeerReviewNode:
    def __init__(self, hypo_row):
        # hypo_row.keys() = dict_keys(['id', 'created', 'updated', 'user', 'uri', 'text', 'tags', 'group', 'permissions', 'target', 'document', 'links', 'user_info', 'flagged', 'moderation', 'hidden'])
        # self.links = {'html': 'https://hypothes.is/a/ChtnSEQXEeygzff7nOkaag', 'incontext': 'https://hyp.is/ChtnSEQXEeygzff7nOkaag/www.biorxiv.org/content/10.1101/2021.08.21.457202v2', 'json': 'https://hypothes.is/api/annotations/ChtnSEQXEeygzff7nOkaag'}
        self._resp = hypo_row
        self.label = 'PeerReviewMaterial'
        self.properties = {}
        self.update_properties({
            'posting_date': self.posting_date,
            'text': self.text,
            'related_article_uri': self.related_article,
            'related_article_doi': self.related_doi,
            'hypothesis_id': self.hypothesis_id,
            'tags': self.tags,
            'link_html': self.link_html,
            'link_json': self.link_json,
            'link_incontext': self.link_incontext,
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
    def hypothesis_id(self):
        return self._resp.get('id', '')

    @property
    def tags(self):
        return self._resp.get('tags', [])

    @property
    def related_doi(self):
        doi = doi_from_uri(self.related_article)
        return doi

    @property
    def link_html(self):
        return self._resp['links'].get('html', '')

    @property
    def link_incontext(self):
        return self._resp['links'].get('incontext', '')

    @property
    def link_json(self):
        return self._resp['links'].get('json', '')


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


class CrossRefReviewNode(JSONNode):

    template = Template('''This study has been evaluated by _${reviewed_by}_.\n\n__${highlight}__\n\nRead the evaluation $review_idx: https://doi.org/$review_doi''')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_text_content()

    def generate_text_content(self):
        review_doi = self.properties.get('doi')
        reviewed_by = self.properties.get('reviewed_by')
        highlight = self.properties.get('highlight')
        review_idx = self.properties.get('review_idx', '')
        review_idx = f"(#{review_idx})" if review_idx else ''
        text = self.template.substitute({
            'reviewed_by': reviewed_by,
            'review_idx': review_idx,
            'review_doi': review_doi,
            'highlight': highlight,
        })
        self.properties['text'] = text


class BioRxiv(API):
    def __init__(self):
        super().__init__()

    def details(self, doi: str, biorxiv_medrxiv: str = 'biorxiv') -> Dict:
        url = f'https://api.biorxiv.org/details/{biorxiv_medrxiv}/{doi}'
        response = self.rest2data(url)
        if response.get('messages', []):
            if response['messages'][0].get('status', '') == 'ok':
                response = response.get('collection', [])[0]
            else:
                response = {}
        else:
            response = {}
        return response


class CrossRefDOI(API):

    def details(self, doi: str) -> Dict:
        url = f'https://doi.org/{doi}'
        response = self.rest2data(url)
        return response


class CrossRefPeerReview(API):

    def __init__(self):
        self.session_retry = self.requests_retry_session(
            retries=5,
            backoff_factor=1.0,
        )
        self.session_retry.headers.update({
            "Accept": "application/json",
            "From": "thomas.lemberger@embo.org"
        })

    def details(self, prefix: str, type_filter: str, limit: int) -> Dict:
        url_summary = f'https://api.crossref.org/prefixes/{prefix}/works'
        params = {
            'rows': 0
        }
        if type_filter:
            # CrossRef API does not accept empty values for filter parameter
            params['filter'] = type_filter
        summary_results = self.rest2data(url_summary, params)
        items = []
        if summary_results.get('status') == 'ok':
            total_results = summary_results['message']['total-results']
            limit = limit if limit else total_results
            items_per_page = min(1000, limit)
            check = 0
            logger.info(f"total_results: %s", total_results)
            # deep paggin with cursor https://github.com/CrossRef/rest-api-doc#result-controls
            cursor = "*"
            params = {'rows': items_per_page}
            if type_filter:
                # CrossRef API does not accept empty values for filter parameter
                params['filter'] = type_filter
            url = f'https://api.crossref.org/prefixes/{prefix}/works'
            while cursor:
                params['cursor'] = cursor
                response = self.rest2data(url, params)
                if response.get('status') == 'ok':
                    new_items = response['message']['items']
                    items += new_items
                    check += len(new_items)
                    if (len(new_items) < items_per_page) or (check >= limit):  # the end has been reached
                        cursor = ''
                    else:
                        cursor = response['message']['next-cursor']
                else:
                    logger.error(response)
                    cursor = ''
                time.sleep(1.0)
            assert check == total_results or check <= limit
        return items


class PeerReviewFinder:

    def __init__(self, db):
        self.db = db
        self.biorxiv = BioRxiv()
        self.crossref_doi = CrossRefDOI()

    def run(self):
        raise NotImplementedError

    def add_prelim_article(self, doi):
        # exists?
        q = MATCH_DOI(params={'doi': doi})
        if not self.db.exists(q):
            # fetch metadata from bioRxiv and CrossRef
            data = self.crossref_doi.details(doi)
            if data:
                logger.info(f"parsing metadata for doi={doi}")
                prelim = JSONNode(data, CROSSREF_PREPRINT_API_GRAPH_MODEL)
                # using biorxiv api here because abstract is plain text while CrossRef has jats namespaced formatting tags
                biorxiv_medrxiv = prelim.properties['journal_title']
                data_biorxiv = self.biorxiv.details(doi, biorxiv_medrxiv.lower())
                if data_biorxiv:
                    prelim.properties['abstract'] = data_biorxiv.get('abstract','abstract not available')
                    prelim.properties['version'] = data_biorxiv['version']
                else:
                    logger.error(f"problem with biorxiv obtaining abstract from doi: {doi}")
                build_neo_graph(prelim, 'biorxiv_crossref', self.db)
            else:
                logger.error(f"problem with crossref to get preprint with doi={doi}")

    def make_relationships(self):
        N_rev = self.db.query(LINK_REVIEWS())
        N_resp = self.db.query(LINK_RESPONSES())
        N_annot = self.db.query(LINK_ANNOT())
        logger.info(f"{N_rev} reviews linked, {N_resp} responses linked, {N_annot} further annotations linked")


class Hypothelink(PeerReviewFinder):

    def __init__(self, db, hypo):
        super().__init__(db)
        self.hypo = hypo

    def run(self, group_ids):
        for group_id in group_ids:
            all_peer_review_nodes = self.get_peer_review_nodes(group_id)
            peer_review_nodes = self.filter_duplicates(all_peer_review_nodes)
            self.merge_peer_review_nodes(peer_review_nodes)
        self.make_relationships()

    def get_peer_review_nodes(self, group_id):
        hypo_rows = self.get_annot_from_hypo(group_id)
        peer_review_nodes = []
        for row in hypo_rows:
            peer_review_node = self.hypo2node(row)
            if peer_review_node is not None and peer_review_node.properties['related_article_doi'] is not None:
                peer_review_node.update_properties({'reviewed_by': HYPO_GROUP_IDS[group_id]})
                peer_review_nodes.append(peer_review_node)
            else:
                logger.warning(f"null or orphan review with annotation: {row['links']}")
        return peer_review_nodes

    def filter_duplicates(self, peer_review_nodes):
        # group reviews by the article they review
        reviews_by_article_doi = {}
        for review in peer_review_nodes:
            related_article_doi = review.properties['related_article_doi']
            reviews_by_article_doi.setdefault(related_article_doi, [])
            reviews_by_article_doi[related_article_doi].append(review)

        non_duplicates = []
        # for each review group: check for duplicates by comparing the review index and text
        for related_article_doi, reviews in reviews_by_article_doi.items():
            review_hashes = set([
                hash((review.properties.get('review_idx', None), review.properties['text']))
                for review in reviews
            ])
            has_duplicates = len(review_hashes) != len(reviews)
            # if any duplicates are found within a group, put all reviews from that group into the duplicates
            if has_duplicates:
                logger.error(f"Article with DOI {related_article_doi} has multiple reviews posted on hypothes.is")
            else:
                non_duplicates.extend(reviews)

        return non_duplicates

    def merge_peer_review_nodes(self, peer_review_nodes):
        for peer_review_node in peer_review_nodes:
            self.db.node(peer_review_node, clause="MERGE")
            logger.info(f"loaded {peer_review_node.label} for {peer_review_node.properties['related_article_doi']}")
            # check if article node missing and add temporary one with source='biorxiv_crossref'
            self.add_prelim_article(peer_review_node.related_doi)


    @staticmethod
    def hypo2node(hypo_row):
        annot_type = type_of_annotation(hypo_row)
        if annot_type == 'review':
            return ReviewCommonsReviewNode(hypo_row)
        elif annot_type == 'response':
            return ReviewCommonsResponseNode(hypo_row)
        elif annot_type == 'peer review material':
            return PeerReviewNode(hypo_row)
        else:
            return None

    def get_annot_from_hypo(self, group_id: str):
        # https://api.hypothes.is/api/search?group=NEGQVabn
        num_annotations_fetched = 0
        limit = 200
        sort = 'updated'
        order = 'asc'
        search_after = ''
        while True:
            response = self.hypo.annotations.search(
                group=group_id,
                limit=limit,
                sort=sort,
                order=order,
                search_after=search_after,
            )
            if response.status_code != 200:
                logger.error(
                    'Fetching annotations after %s from hypothes.is failed for group %s: %s, %s',
                    search_after,
                    HYPO_GROUP_IDS[group_id],
                    response.status_code,
                    response.text,
                )
                return

            response_json = response.json()
            num_annotations_reported_by_hypothesis = response_json['total']
            annotations = response_json['rows']
            num_annotations = len(annotations)
            # no annotations in the result means we've gotten all annotations.
            if num_annotations == 0:
                if num_annotations_fetched == num_annotations_reported_by_hypothesis:
                    logger.info(
                        'Fetched all %s annotations for group %s',
                        num_annotations_fetched,
                        HYPO_GROUP_IDS[group_id],
                    )
                else:
                    logger.error(
                        'hypothes.is reported having %s annotations for group %s but we fetched %s',
                        num_annotations_reported_by_hypothesis,
                        HYPO_GROUP_IDS[group_id],
                        num_annotations_fetched,
                    )
                return

            num_annotations_fetched += num_annotations
            logger.info(
                'Fetched %s of %s annotations for group %s',
                num_annotations_fetched,
                num_annotations_reported_by_hypothesis,
                HYPO_GROUP_IDS[group_id],
            )
            for annotation in annotations:
                yield annotation

            # The annotations are sorted in ascending order by their last update,
            # therefore the newest annotation of this page is the last one.
            newest_annotation = annotations[-1]
            # update the search parameter to only find annotations after the newest
            # annotation on this page. The hypothes.is API says it returns "the record
            # immediately subsequent to the annotation created at [the search_after
            # parameter]". It does not comment on annotations updated at the same time
            # so we might have a possible bug: if two annotations were updated at the
            # same time but sit on different pages we might not get the 2nd one.
            search_after = newest_annotation['updated']


def is_cross_ref_review(r, target_prefixes):
    peer_review_of = r.get('relation', {}).get('is-review-of', [])
    if peer_review_of:
        is_review_of_this_doi = peer_review_of[0]['id']
        reg = re.match(r'^(\d+\.\d+)/', is_review_of_this_doi)
        if reg:
            prefix = reg.group(1)
            if prefix in target_prefixes:
                return prefix
    return False


class CrossRefReviewFinder(PeerReviewFinder):

    MODELS = {
        '10.1162': CROSSREF_PEERREVIEW_GRAPH_MODEL,
        '10.24072': CROSSREF_PCI_REVIEW_GRAPH_MODEL,
        '10.7554': CROSSREF_PEERREVIEW_GRAPH_MODEL,
    }

    def __init__(self, db):
        super().__init__(db)
        self.crossref_peer_review = CrossRefPeerReview()

    def run(self, source_prefix, target_prefixes, type_filter, limit):
        items = self.crossref_peer_review.details(source_prefix, type_filter, limit)
        for item in items:
            if is_cross_ref_review(item, target_prefixes):
                try:
                    peer_review_node = CrossRefReviewNode(item, self.MODELS[source_prefix])
                except Exception as e:
                    logger.error("Failed to parse Crossref data into CrossRefReviewNode: %s", item, exc_info=1)
                    continue
                logger.debug(peer_review_node)
                build_neo_graph(peer_review_node, 'cross_ref', self.db)
                self.add_prelim_article(peer_review_node.properties['related_article_doi'])
        self.make_relationships()


if __name__ == '__main__':
    common.logging.configure_logging()
    parser = ArgumentParser(description="Upload peer review material using CrossRef. Identifies reviews produced by source on papers/preprints published by target.")
    parser.add_argument('source', default='', help='Name of the reviewing service (source) to scan.')
    parser.add_argument('-T', '--target', default='biorxiv', help='DOI prefix of the published reviewed papers (target).')
    parser.add_argument('-L', '--limit', default='', help='Limit the number of results for debugging')
    args = parser.parse_args()
    source = args.source
    target = args.target
    limit = args.limit
    limit = int(limit) if limit else None
    SOURCE_PREFIXES = {
        'pci': '10.24072',
        'rrc19': '10.1162',
        'elife': '10.7554',
    }
    TARGET_PREFIXES = {
        'biorxiv': '10.1101',
        'elife': '10.7554',
    }
    if source == 'pci':
        CrossRefReviewFinder(DB).run(SOURCE_PREFIXES[source.lower()], [TARGET_PREFIXES[target.lower()]], type_filter='', limit=limit)
    elif source == 'rrc19':
        CrossRefReviewFinder(DB).run(SOURCE_PREFIXES[source.lower()], [TARGET_PREFIXES[target.lower()]], type_filter='type:peer-review', limit=limit)
    elif source == 'hypothesis':
        Hypothelink(DB, HYPO).run(HYPO_GROUP_IDS)
    else:
        logger.info("no model yet for this source")
