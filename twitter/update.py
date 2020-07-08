import argparse
import tweepy
from string import Template
from sdg.sdnode import API
from .queries import TWEET_BY_DOI, ADD_TWITTER_STATUS
from typing import Dict
from . import DB, TWITTER, EEB_PUBLIC_API, logger


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
        self.text = self.template.substitute(self.substitutions)

    def __str__(self):
        return self.text


class RefereedPreprintContent(Content):

    template = Template('''#RefereedPreprint by $reviewed_by_twitter_handle \n$title \nPreprint doi: https://doi.org/$preprint_doi''')
    handles = {
        'review commons': '@ReviewCommons',
        'elife': '@eLife',
        'peerage of scienec': '@peeragescience',
        'embo press': '@embopress',
    }

    def __init__(self, result):
        super().__init__(result)
        # self.published_doi = self.result.get('journal_doi', '')
        # self.published_journal_title = self.result.get('published_journal_title', '')
        if self.result['review_process']['reviews']:
            self.reviewed_by_twitter_handle = self.handles[self.result['review_process']['reviews'][0]['reviewed_by']]
        elif self.result['review_process']['annot']:
            self.reviewed_by_twitter_handle = self.handles[self.result['review_process']['annot']['reviewed_by']]
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

    def __init__(self, db, twitter, eeb_method, ContentClass):
        self.db = db
        self.twitter = twitter
        self.eeb_by_doi = EEB_API().by_doi
        self.eeb_method = eeb_method
        self.ContentClass = ContentClass

    def to_be_tweeted(self, limit_date: str):
        results = self.eeb_method(limit_date)
        not_yet_tweeted = self.filter_not_tweeted(results)
        return not_yet_tweeted

    def filter_not_tweeted(self, results):
        filtered = []
        for collection in results:
            for r in collection['papers']:
                doi = r['doi']
                already_tweeted = self.db.exists(TWEET_BY_DOI(params={'doi': doi}))
                if not already_tweeted:
                    filtered.append(doi)
        return filtered

    def update_status(self, dois):
        for doi in dois:
            # fetch the full record, include reviews etc..
            record = self.eeb_by_doi(doi)
            # parse the record to extract what is necessary to make tweet content
            content = self.ContentClass(record[0])
            # update the status with this content
            try:
                status = self.twitter.update_status(str(content))
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
            except tweepy.error.TweepError as e:
                print(e)
                logger.error(str(e))

    def run(self, limit_date: str):
        dois = self.to_be_tweeted(limit_date)
        self.update_status(dois)


def main():
    parser = argparse.ArgumentParser(description="Post eeb highlights on Twitter.")
    parser.add_argument('--limit-date', help='Limit the post for preprint posted after the limit date') # TODO: pub_limit_date vs review_limit_date
    args = parser.parse_args()
    limit_date = args.limit_date
    t1 = Twitterer(DB, TWITTER, EEB_API().get_refereed_preprints, RefereedPreprintContent)
    t1.run(limit_date=limit_date)
    # t2 = Twitterer(DB, TWITTER, EEB_API().get_by_hyp, ByHypContent)
    # t2.run(limit_date=limit_date)


if __name__ == '__main__':
    main()
