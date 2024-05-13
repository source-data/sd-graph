from argparse import ArgumentParser
from pandas import DataFrame, concat, read_csv, to_datetime
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import common.logging
from peerreview.neohypo import BioRxiv, CrossRefDOI
from sdg.sdnode import API
from . import DB
from .queries import (
    NotYetPublished, UpdatePublicationStatus,
)

logger = common.logging.get_logger(__name__)


def _date_from_parts(parts):
    if len(parts) < 1 or len(parts) > 3:
        return None
    if len(parts) == 1:
        parts.append(1)
        parts.append(1)
    if len(parts) == 2:
        parts.append(1)
    return f"{parts[0]}-{parts[1]}-{parts[2]}"


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
        raise NotImplementedError()

    def update_status(self, preprint_doi, published_doi):
        cross_ref_metadata = self.crossref.details(published_doi)
        published_journal_title = cross_ref_metadata.get('container-title', '')
        published_date = _date_from_parts(cross_ref_metadata.get('published', {}).get('date-parts', [[]])[0])

        params = {
            'preprint_doi': preprint_doi,
            'published_doi': published_doi,
            'published_journal_title': published_journal_title,
            'published_date': published_date,
        }
        update_published_status = UpdatePublicationStatus(params=params)
        self.db.query(update_published_status)
        return published_journal_title, published_date

    def run(self, limit_date: str):
        not_yet_published = self.get_not_published(limit_date)
        logger.info(f"{len(not_yet_published)} preprints posted since {limit_date} with no journal publication info yet.")
        with logging_redirect_tqdm():
            for preprint_doi in tqdm(not_yet_published):
                published_doi = self.check_publication_status(preprint_doi)
                if (published_doi is not None) and (published_doi != "NA"):
                    journal, date = self.update_status(preprint_doi, published_doi)
                    logger.info(f"{preprint_doi} --> {published_doi} in {journal} on {date}")


class BiorxivPubUpdate(PublicationUpdate):
    def check_publication_status(self, preprint_doi):
        published_doi = self.biorxiv.details(preprint_doi).get('published', None)
        return published_doi


class CrossRefPreprintApi(API):
    def __init__(self):
        super().__init__()
        self.url = 'https://api.crossref.org/types/posted-content/works'
        self._cache_file = 'crossref_preprints.csv'
        self._data = None

    def _published_preprints(self):
        if self._data is None:
            try:
                data = read_csv(self._cache_file)
                latest_index_date = to_datetime(data['index_date'].max()).strftime('%Y-%m-%d')
            except FileNotFoundError:
                data = None
                latest_index_date = None

            new_data = self._new_data(latest_index_date)
            if data is None:
                self._data = new_data
            else:
                self._data = (
                    concat([data, new_data])
                    .drop_duplicates(subset='preprint_doi', keep='last')
                    .sort_values(['index_date', 'preprint_doi'], ascending=False)
                    .reset_index(drop=True)
                )

            self._data.to_csv(self._cache_file, index=False)
        return self._data

    def _new_data(self, latest_index_date):
        params = {
            'filter': 'relation.type:is-preprint-of',
            'select': 'DOI,indexed,relation',
            'rows': 1000,
            'cursor': '*',
        }
        if latest_index_date:
            params['filter'] += f',from-index-date:{latest_index_date}'

        new_data = []
        n_items_fetched = 0
        while True:
            message = self.rest2data(self.url, params).get('message', {})
            items = message.get('items', [])
            if not items:
                break

            n_items_fetched += len(items)
            logger.info(f"Fetched {n_items_fetched}/{message['total-results']} items from CrossRef API.")

            for item in items:
                relation = item['relation']['is-preprint-of'][0]
                if relation['id-type'] != 'doi':
                    continue
                preprint_doi = item['DOI']
                published_doi = relation['id']
                indexed_date = _date_from_parts(item['indexed']['date-parts'][0])
                new_data.append({
                    'preprint_doi': preprint_doi,
                    'published_doi': published_doi,
                    'index_date': indexed_date,
                })

            next_cursor = message.get('next-cursor', None)
            params['cursor'] = next_cursor

        return DataFrame(new_data)


class CrossRefPubUpdate(PublicationUpdate):
    def __init__(self, db):
        super().__init__(db)
        self.crossref_preprints = CrossRefPreprintApi()

    def check_publication_status(self, preprint_doi):
        data = self.crossref_preprints._published_preprints()
        published_dois = data.loc[data['preprint_doi'] == preprint_doi, 'published_doi']
        if len(published_dois) == 0:
            return None
        elif len(published_dois) > 1:
            logger.warning(f"Multiple published DOIs for preprint {preprint_doi}: {published_dois}")
        return published_dois.iat[0]


def main():
    parser = ArgumentParser(description="Upload reviews linked to preprints and updates publication status of preprints.")
    parser.add_argument('--limit-date', default='1900-01-01', help='Limit posting date: only preprints older than this limit date will be scanned for journal publication status.')
    args = parser.parse_args()
    limit_date = args.limit_date
    BiorxivPubUpdate(DB).run(limit_date=limit_date)
    CrossRefPubUpdate(DB).run(limit_date=limit_date)


if __name__ == '__main__':
    common.logging.configure_logging()
    main()
