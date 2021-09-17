from argparse import ArgumentParser
from tqdm import tqdm
import common.logging
from peerreview.neohypo import BioRxiv, CrossRefDOI
from . import DB
from .queries import (
    NotYetPublished, UpdatePublicationStatus,
)

logger = common.logging.get_logger(__name__)

class PublicationUpdate:

    def __init__(self, db):
        self.db = db
        self.biorxiv = BioRxiv()
        self.crossref = CrossRefDOI()

    def get_not_published(self, limit_date: str):
        results = self.db.query(NotYetPublished(params={'limit_date': limit_date}))
        dois = [r['doi'] for r in results]
        return dois

    def check_publication_status(self, preprint_doi):
        published_doi = self.biorxiv.details(preprint_doi).get('published', None)
        return published_doi

    def update_status(self, preprint_doi, published_doi):
        cross_ref_metadata = self.crossref.details(published_doi)
        published_journal_title = cross_ref_metadata.get('container-title', '')
        params = {
            'preprint_doi': preprint_doi,
            'published_doi': published_doi,
            'published_journal_title': published_journal_title,
        }
        update_published_status = UpdatePublicationStatus(params=params)
        self.db.query(update_published_status)
        return published_journal_title

    def run(self, limit_date: str):
        not_yet_published = self.get_not_published(limit_date)
        logger.info(f"{len(not_yet_published)} preprints posted since {limit_date} with no journal publication info yet.")
        msg = ''
        N = len(not_yet_published)
        for preprint_doi in tqdm(not_yet_published):
            published_doi = self.check_publication_status(preprint_doi)
            if (published_doi is not None) and (published_doi != "NA"):
                journal = self.update_status(preprint_doi, published_doi)


def main():
    parser = ArgumentParser(description="Upload reviews linked to preprints and updates publication status of preprints.")
    parser.add_argument('--limit-date', default='1900-01-01', help='Limit posting date: only preprints older than this limit date will be scanned for journal publication status.')
    args = parser.parse_args()
    limit_date = args.limit_date
    PublicationUpdate(DB).run(limit_date=limit_date)


if __name__ == '__main__':
    common.logging.configure_logging()
    main()
