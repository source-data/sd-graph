# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.author import Author  # noqa: F401,E501
from swagger_server import util


class RefereedPreprint(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, doi: str=None, version: str=None, source: str=None, journal: str=None, title: str=None, abstract: str=None, journal_doi: str=None, published_journal_title: str=None, pub_date: datetime=None, authors: List[Author]=None, review_dates: List[datetime]=None, entities: List[str]=None, assays: List[str]=None, main_topics: List[List[str]]=None, highlighted_entities: List[str]=None, slug: str=None, reviewed_by: List[str]=None):  # noqa: E501
        """RefereedPreprint - a model defined in Swagger

        :param doi: The doi of this RefereedPreprint.  # noqa: E501
        :type doi: str
        :param version: The version of this RefereedPreprint.  # noqa: E501
        :type version: str
        :param source: The source of this RefereedPreprint.  # noqa: E501
        :type source: str
        :param journal: The journal of this RefereedPreprint.  # noqa: E501
        :type journal: str
        :param title: The title of this RefereedPreprint.  # noqa: E501
        :type title: str
        :param abstract: The abstract of this RefereedPreprint.  # noqa: E501
        :type abstract: str
        :param journal_doi: The journal_doi of this RefereedPreprint.  # noqa: E501
        :type journal_doi: str
        :param published_journal_title: The published_journal_title of this RefereedPreprint.  # noqa: E501
        :type published_journal_title: str
        :param pub_date: The pub_date of this RefereedPreprint.  # noqa: E501
        :type pub_date: datetime
        :param authors: The authors of this RefereedPreprint.  # noqa: E501
        :type authors: List[Author]
        :param review_dates: The review_dates of this RefereedPreprint.  # noqa: E501
        :type review_dates: List[datetime]
        :param entities: The entities of this RefereedPreprint.  # noqa: E501
        :type entities: List[str]
        :param assays: The assays of this RefereedPreprint.  # noqa: E501
        :type assays: List[str]
        :param main_topics: The main_topics of this RefereedPreprint.  # noqa: E501
        :type main_topics: List[List[str]]
        :param highlighted_entities: The highlighted_entities of this RefereedPreprint.  # noqa: E501
        :type highlighted_entities: List[str]
        :param slug: The slug of this RefereedPreprint.  # noqa: E501
        :type slug: str
        :param reviewed_by: The reviewed_by of this RefereedPreprint.  # noqa: E501
        :type reviewed_by: List[str]
        """
        self.swagger_types = {
            'doi': str,
            'version': str,
            'source': str,
            'journal': str,
            'title': str,
            'abstract': str,
            'journal_doi': str,
            'published_journal_title': str,
            'pub_date': datetime,
            'authors': List[Author],
            'review_dates': List[datetime],
            'entities': List[str],
            'assays': List[str],
            'main_topics': List[List[str]],
            'highlighted_entities': List[str],
            'slug': str,
            'reviewed_by': List[str]
        }

        self.attribute_map = {
            'doi': 'doi',
            'version': 'version',
            'source': 'source',
            'journal': 'journal',
            'title': 'title',
            'abstract': 'abstract',
            'journal_doi': 'journal_doi',
            'published_journal_title': 'published_journal_title',
            'pub_date': 'pub_date',
            'authors': 'authors',
            'review_dates': 'review_dates',
            'entities': 'entities',
            'assays': 'assays',
            'main_topics': 'main_topics',
            'highlighted_entities': 'highlighted_entities',
            'slug': 'slug',
            'reviewed_by': 'reviewed_by'
        }
        self._doi = doi
        self._version = version
        self._source = source
        self._journal = journal
        self._title = title
        self._abstract = abstract
        self._journal_doi = journal_doi
        self._published_journal_title = published_journal_title
        self._pub_date = pub_date
        self._authors = authors
        self._review_dates = review_dates
        self._entities = entities
        self._assays = assays
        self._main_topics = main_topics
        self._highlighted_entities = highlighted_entities
        self._slug = slug
        self._reviewed_by = reviewed_by

    @classmethod
    def from_dict(cls, dikt) -> 'RefereedPreprint':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The RefereedPreprint of this RefereedPreprint.  # noqa: E501
        :rtype: RefereedPreprint
        """
        return util.deserialize_model(dikt, cls)

    @property
    def doi(self) -> str:
        """Gets the doi of this RefereedPreprint.

        The DOI of the refereed preprint.  # noqa: E501

        :return: The doi of this RefereedPreprint.
        :rtype: str
        """
        return self._doi

    @doi.setter
    def doi(self, doi: str):
        """Sets the doi of this RefereedPreprint.

        The DOI of the refereed preprint.  # noqa: E501

        :param doi: The doi of this RefereedPreprint.
        :type doi: str
        """

        self._doi = doi

    @property
    def version(self) -> str:
        """Gets the version of this RefereedPreprint.

        The version of the refereed preprint.  # noqa: E501

        :return: The version of this RefereedPreprint.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version: str):
        """Sets the version of this RefereedPreprint.

        The version of the refereed preprint.  # noqa: E501

        :param version: The version of this RefereedPreprint.
        :type version: str
        """

        self._version = version

    @property
    def source(self) -> str:
        """Gets the source of this RefereedPreprint.

        The source of the refereed preprint. Either \"bioRxiv\" or \"medRxiv\".  # noqa: E501

        :return: The source of this RefereedPreprint.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source: str):
        """Sets the source of this RefereedPreprint.

        The source of the refereed preprint. Either \"bioRxiv\" or \"medRxiv\".  # noqa: E501

        :param source: The source of this RefereedPreprint.
        :type source: str
        """

        self._source = source

    @property
    def journal(self) -> str:
        """Gets the journal of this RefereedPreprint.

        The journal the refereed preprint was published in.  # noqa: E501

        :return: The journal of this RefereedPreprint.
        :rtype: str
        """
        return self._journal

    @journal.setter
    def journal(self, journal: str):
        """Sets the journal of this RefereedPreprint.

        The journal the refereed preprint was published in.  # noqa: E501

        :param journal: The journal of this RefereedPreprint.
        :type journal: str
        """

        self._journal = journal

    @property
    def title(self) -> str:
        """Gets the title of this RefereedPreprint.

        The title of the refereed preprint.  # noqa: E501

        :return: The title of this RefereedPreprint.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this RefereedPreprint.

        The title of the refereed preprint.  # noqa: E501

        :param title: The title of this RefereedPreprint.
        :type title: str
        """

        self._title = title

    @property
    def abstract(self) -> str:
        """Gets the abstract of this RefereedPreprint.

        The abstract of the refereed preprint.  # noqa: E501

        :return: The abstract of this RefereedPreprint.
        :rtype: str
        """
        return self._abstract

    @abstract.setter
    def abstract(self, abstract: str):
        """Sets the abstract of this RefereedPreprint.

        The abstract of the refereed preprint.  # noqa: E501

        :param abstract: The abstract of this RefereedPreprint.
        :type abstract: str
        """

        self._abstract = abstract

    @property
    def journal_doi(self) -> str:
        """Gets the journal_doi of this RefereedPreprint.

        The DOI of the published version of this refereed preprint. Null if the refereed preprint has not been published.  # noqa: E501

        :return: The journal_doi of this RefereedPreprint.
        :rtype: str
        """
        return self._journal_doi

    @journal_doi.setter
    def journal_doi(self, journal_doi: str):
        """Sets the journal_doi of this RefereedPreprint.

        The DOI of the published version of this refereed preprint. Null if the refereed preprint has not been published.  # noqa: E501

        :param journal_doi: The journal_doi of this RefereedPreprint.
        :type journal_doi: str
        """

        self._journal_doi = journal_doi

    @property
    def published_journal_title(self) -> str:
        """Gets the published_journal_title of this RefereedPreprint.

        The title of the journal the refereed preprint was published in. Null if the refereed preprint has not been published.  # noqa: E501

        :return: The published_journal_title of this RefereedPreprint.
        :rtype: str
        """
        return self._published_journal_title

    @published_journal_title.setter
    def published_journal_title(self, published_journal_title: str):
        """Sets the published_journal_title of this RefereedPreprint.

        The title of the journal the refereed preprint was published in. Null if the refereed preprint has not been published.  # noqa: E501

        :param published_journal_title: The published_journal_title of this RefereedPreprint.
        :type published_journal_title: str
        """

        self._published_journal_title = published_journal_title

    @property
    def pub_date(self) -> datetime:
        """Gets the pub_date of this RefereedPreprint.

        The date the refereed preprint was published.  # noqa: E501

        :return: The pub_date of this RefereedPreprint.
        :rtype: datetime
        """
        return self._pub_date

    @pub_date.setter
    def pub_date(self, pub_date: datetime):
        """Sets the pub_date of this RefereedPreprint.

        The date the refereed preprint was published.  # noqa: E501

        :param pub_date: The pub_date of this RefereedPreprint.
        :type pub_date: datetime
        """

        self._pub_date = pub_date

    @property
    def authors(self) -> List[Author]:
        """Gets the authors of this RefereedPreprint.

        The authors of the refereed preprint.  # noqa: E501

        :return: The authors of this RefereedPreprint.
        :rtype: List[Author]
        """
        return self._authors

    @authors.setter
    def authors(self, authors: List[Author]):
        """Sets the authors of this RefereedPreprint.

        The authors of the refereed preprint.  # noqa: E501

        :param authors: The authors of this RefereedPreprint.
        :type authors: List[Author]
        """

        self._authors = authors

    @property
    def review_dates(self) -> List[datetime]:
        """Gets the review_dates of this RefereedPreprint.

        The dates the refereed preprint was reviewed on.  # noqa: E501

        :return: The review_dates of this RefereedPreprint.
        :rtype: List[datetime]
        """
        return self._review_dates

    @review_dates.setter
    def review_dates(self, review_dates: List[datetime]):
        """Sets the review_dates of this RefereedPreprint.

        The dates the refereed preprint was reviewed on.  # noqa: E501

        :param review_dates: The review_dates of this RefereedPreprint.
        :type review_dates: List[datetime]
        """

        self._review_dates = review_dates

    @property
    def entities(self) -> List[str]:
        """Gets the entities of this RefereedPreprint.

        The entities (e.g. genes, proteins, diseases) mentioned in the refereed preprint's figures.  # noqa: E501

        :return: The entities of this RefereedPreprint.
        :rtype: List[str]
        """
        return self._entities

    @entities.setter
    def entities(self, entities: List[str]):
        """Sets the entities of this RefereedPreprint.

        The entities (e.g. genes, proteins, diseases) mentioned in the refereed preprint's figures.  # noqa: E501

        :param entities: The entities of this RefereedPreprint.
        :type entities: List[str]
        """

        self._entities = entities

    @property
    def assays(self) -> List[str]:
        """Gets the assays of this RefereedPreprint.

        The assays (e.g. ELISA, PCR) mentioned in the refereed preprint's figures.  # noqa: E501

        :return: The assays of this RefereedPreprint.
        :rtype: List[str]
        """
        return self._assays

    @assays.setter
    def assays(self, assays: List[str]):
        """Sets the assays of this RefereedPreprint.

        The assays (e.g. ELISA, PCR) mentioned in the refereed preprint's figures.  # noqa: E501

        :param assays: The assays of this RefereedPreprint.
        :type assays: List[str]
        """

        self._assays = assays

    @property
    def main_topics(self) -> List[List[str]]:
        """Gets the main_topics of this RefereedPreprint.

        The main topics of the refereed preprint.  # noqa: E501

        :return: The main_topics of this RefereedPreprint.
        :rtype: List[List[str]]
        """
        return self._main_topics

    @main_topics.setter
    def main_topics(self, main_topics: List[List[str]]):
        """Sets the main_topics of this RefereedPreprint.

        The main topics of the refereed preprint.  # noqa: E501

        :param main_topics: The main_topics of this RefereedPreprint.
        :type main_topics: List[List[str]]
        """

        self._main_topics = main_topics

    @property
    def highlighted_entities(self) -> List[str]:
        """Gets the highlighted_entities of this RefereedPreprint.

        The highlighted entities (e.g. genes, proteins, diseases) mentioned in the refereed preprint's abstract.  # noqa: E501

        :return: The highlighted_entities of this RefereedPreprint.
        :rtype: List[str]
        """
        return self._highlighted_entities

    @highlighted_entities.setter
    def highlighted_entities(self, highlighted_entities: List[str]):
        """Sets the highlighted_entities of this RefereedPreprint.

        The highlighted entities (e.g. genes, proteins, diseases) mentioned in the refereed preprint's abstract.  # noqa: E501

        :param highlighted_entities: The highlighted_entities of this RefereedPreprint.
        :type highlighted_entities: List[str]
        """

        self._highlighted_entities = highlighted_entities

    @property
    def slug(self) -> str:
        """Gets the slug of this RefereedPreprint.

        The slug of the refereed preprint. Can be used to construct a URL to the refereed preprint's page on the Early Evidence Base platform.  # noqa: E501

        :return: The slug of this RefereedPreprint.
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug: str):
        """Sets the slug of this RefereedPreprint.

        The slug of the refereed preprint. Can be used to construct a URL to the refereed preprint's page on the Early Evidence Base platform.  # noqa: E501

        :param slug: The slug of this RefereedPreprint.
        :type slug: str
        """

        self._slug = slug

    @property
    def reviewed_by(self) -> List[str]:
        """Gets the reviewed_by of this RefereedPreprint.

        The IDs of the reviewing services that reviewed this refereed preprint.  # noqa: E501

        :return: The reviewed_by of this RefereedPreprint.
        :rtype: List[str]
        """
        return self._reviewed_by

    @reviewed_by.setter
    def reviewed_by(self, reviewed_by: List[str]):
        """Sets the reviewed_by of this RefereedPreprint.

        The IDs of the reviewing services that reviewed this refereed preprint.  # noqa: E501

        :param reviewed_by: The reviewed_by of this RefereedPreprint.
        :type reviewed_by: List[str]
        """

        self._reviewed_by = reviewed_by