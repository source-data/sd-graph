import argparse
import tweepy
from string import Template
import time
import common.logging
from sdg.sdnode import API
from neotools.utils import progress
from .queries import TWEET_BY_DOI, ADD_TWITTER_STATUS
from typing import Dict
from . import DB, TWITTER, EEB_PUBLIC_API

logger = common.logging.get_logger(__name__)


TWITTER_MAX_LENGTH = 280


class Content:

    template: Template = None

    def __init__(self, result):
        # ['preprint_doi', 'title', 'preprint_date', 'published_doi', 'published_journal_title', 'review_by', 'annot_by']
        self.text = ''
        self.result = result
        self.title = self.result['title']
        self.preprint_doi = self.result['doi']
        self.text = ''
        self.substitutions = {}
        self.update_substitutions({
            'title': self.title,
            'preprint_doi': self.preprint_doi
        })

    def update_substitutions(self, d: Dict):
        self.substitutions = {**self.substitutions, **d}

    def update_text(self):
        text = self.template.substitute(self.substitutions)
        L = len(text)
        if L > TWITTER_MAX_LENGTH:
            diff = L - TWITTER_MAX_LENGTH + 3
            self.substitutions['title'] = self.substitutions['title'][:-diff] + '...'
            text = self.template.substitute(self.substitutions)
        self.text = text

    def __str__(self):
        return self.text


class RefereedPreprintContent(Content):

    template = Template('''#RefereedPreprint by $reviewed_by_twitter_handle \n$title \nPreprint doi: https://doi.org/$preprint_doi''')
    mentions = {
        'review commons': 'Review Commons',
        'elife': 'eLife',
        'peerage of science': 'Peerage of Science',
        'embo press': 'EMBO Press',
    }

    def __init__(self, result):
        super().__init__(result)
        if self.result['review_process']['reviews']:
            self.reviewed_by_twitter_handle = self.mentions[self.result['review_process']['reviews'][0]['reviewed_by']]
        elif self.result['review_process']['annot']:
            self.reviewed_by_twitter_handle = self.mentions[self.result['review_process']['annot']['reviewed_by']]
        self.update_substitutions({
            'reviewed_by_twitter_handle': self.reviewed_by_twitter_handle,
        })
        self.update_text()


class ByHypContent(Content):

    template = Template('$title, preprint doi: https://doi.org/$preprint_doi')

    def __init__(self, result):

        self.result['']['']
        self.update_substitutions({
        })
        self.text = self.template.substitute(self.substitution)


class AutomagicSelectionContent(Content):

    template = Template('Autoselection: $title, preprint doi: https://doi.org/$preprint_doi')

    def __init__(self, result):
        super().__init__(result)
        self.text = self.template.substitute(self.substitution)


class EEB_API(API):

    BASE_URL = EEB_PUBLIC_API
    BY_REVIEWING_SERVICE = 'by_reviewing_service/'
    BY_HYP = 'by_hyp/'
    AUTOMAGIC = 'automagic/'
    BY_DOI = 'doi/'

    def get_refereed_preprints(self, limit_date: str):
        return self.rest2data(self.BASE_URL + self.BY_REVIEWING_SERVICE + limit_date)

    def get_by_hyp(self, limit_date: str):
        return self.rest2data(self.BASE_URL + self.BY_HYP + limit_date)

    def automagic_selection(self, limit_date: str):
        return self.rest2data(self.BASE_URL + self.AUTOMAGIC + limit_date)

    def by_doi(self, doi: str):
        return self.rest2data(self.BASE_URL + self.BY_DOI + doi)


class Twitterer:

    def __init__(self, db, twitter, eeb_method, ContentClass, debug=True):
        self.db = db
        self.twitter = twitter
        self.eeb_by_doi = EEB_API().by_doi
        self.eeb_method = eeb_method
        self.ContentClass = ContentClass
        self.debug = debug

    def to_be_tweeted(self, limit_date: str):
        results = self.eeb_method(limit_date)
        unpublished_records = self.filter_unpublished(results)
        not_yet_tweeted_records = self.filter_not_tweeted(unpublished_records)
        return not_yet_tweeted_records

    def filter_unpublished(self, results):
        filtered_records = []
        for collection in results:
            for r in collection['papers']:
                doi = r.get('doi', '')
                record = self.eeb_by_doi(doi)[0]
                already_published = record.get('journal_doi', '')
                if not already_published:
                    filtered_records.append(record)
        return filtered_records

    def filter_not_tweeted(self, records):
        filtered_records = []
        N = len(records)
        for i, record in enumerate(records):
            progress(i, N, "check if already tweeted")
            doi = record['doi']
            already_tweeted = self.db.exists(TWEET_BY_DOI(params={'doi': doi}))
            if not already_tweeted:
                filtered_records.append(record)
        print()
        logger.info(f"{len(filtered_records)} updates to be tweeted.")
        return filtered_records

    def update_status(self, records):
        for record in records:
            # parse the record to extract what is necessary to make tweet content
            content = self.ContentClass(record)
            # update the status with this content
            try:
                if self.debug:
                    logger.info(f"debug mode post: \n{content}")
                    status = False
                else:
                    status = self.twitter.update_status(str(content))
                    time.sleep(24.0)  # max 150 post + 150 delete  per hour: 3600 sec / 150 = 24sec !!
                # keep a copy of the status in the database
                if status:
                    q = ADD_TWITTER_STATUS(
                            params={
                                'related_preprint_doi': content.preprint_doi,
                                'text': status.text,
                                'twitter_id': status.id_str,
                                'created_at': status.created_at.isoformat(),
                                'hashtags': '///'.join([h['text'] for h in status.entities['hashtags']]),
                            }
                        )
                    self.db.query(q)
                    logger.info(f"posted: {status.id_str}")
            except tweepy.error.TweepError as err:
                logger.error(f"problem with doi {content.preprint_doi}: {err.reason}")

    def run(self, limit_date: str):
        dois = self.to_be_tweeted(limit_date)
        self.update_status(dois)


def main():
    parser = argparse.ArgumentParser(description="Post eeb highlights on Twitter.")
    parser.add_argument('--limit-date', default='2020-07-01', help='Limit the post for preprint posted after the limit date')
    parser.add_argument('--GO_LIVE', action='store_true', help='This flag MUST be added to post updates on twitter and switch off debug mode.')
    args = parser.parse_args()
    debug = not args.GO_LIVE
    limit_date = args.limit_date
    t1 = Twitterer(DB, TWITTER, EEB_API().get_refereed_preprints, RefereedPreprintContent, debug=debug)
    t1.run(limit_date=limit_date)


if __name__ == '__main__':
    common.logging.configure_logging()
    main()
