# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.author import Author  # noqa: F401,E501
from swagger_server import util


class Paper(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, doi: str=None, version: str=None, source: str=None, journal: str=None, title: str=None, abstract: str=None, journal_doi: str=None, published_journal_title: str=None, pub_date: datetime=None, authors: List[Author]=None, revdate: datetime=None, entities: List[str]=None, assays: List[str]=None, main_topics: List[List[str]]=None, highlighted_entities: List[str]=None, slug: str=None, reviewed_by: List[str]=None):  # noqa: E501
        """Paper - a model defined in Swagger

        :param doi: The doi of this Paper.  # noqa: E501
        :type doi: str
        :param version: The version of this Paper.  # noqa: E501
        :type version: str
        :param source: The source of this Paper.  # noqa: E501
        :type source: str
        :param journal: The journal of this Paper.  # noqa: E501
        :type journal: str
        :param title: The title of this Paper.  # noqa: E501
        :type title: str
        :param abstract: The abstract of this Paper.  # noqa: E501
        :type abstract: str
        :param journal_doi: The journal_doi of this Paper.  # noqa: E501
        :type journal_doi: str
        :param published_journal_title: The published_journal_title of this Paper.  # noqa: E501
        :type published_journal_title: str
        :param pub_date: The pub_date of this Paper.  # noqa: E501
        :type pub_date: datetime
        :param authors: The authors of this Paper.  # noqa: E501
        :type authors: List[Author]
        :param revdate: The revdate of this Paper.  # noqa: E501
        :type revdate: datetime
        :param entities: The entities of this Paper.  # noqa: E501
        :type entities: List[str]
        :param assays: The assays of this Paper.  # noqa: E501
        :type assays: List[str]
        :param main_topics: The main_topics of this Paper.  # noqa: E501
        :type main_topics: List[List[str]]
        :param highlighted_entities: The highlighted_entities of this Paper.  # noqa: E501
        :type highlighted_entities: List[str]
        :param slug: The slug of this Paper.  # noqa: E501
        :type slug: str
        :param reviewed_by: The reviewed_by of this Paper.  # noqa: E501
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
            'revdate': datetime,
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
            'revdate': 'revdate',
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
        self._revdate = revdate
        self._entities = entities
        self._assays = assays
        self._main_topics = main_topics
        self._highlighted_entities = highlighted_entities
        self._slug = slug
        self._reviewed_by = reviewed_by

    @classmethod
    def from_dict(cls, dikt) -> 'Paper':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Paper of this Paper.  # noqa: E501
        :rtype: Paper
        """
        return util.deserialize_model(dikt, cls)

    @property
    def doi(self) -> str:
        """Gets the doi of this Paper.

        The DOI of the paper.  # noqa: E501

        :return: The doi of this Paper.
        :rtype: str
        """
        return self._doi

    @doi.setter
    def doi(self, doi: str):
        """Sets the doi of this Paper.

        The DOI of the paper.  # noqa: E501

        :param doi: The doi of this Paper.
        :type doi: str
        """

        self._doi = doi

    @property
    def version(self) -> str:
        """Gets the version of this Paper.

        The version of the paper.  # noqa: E501

        :return: The version of this Paper.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version: str):
        """Sets the version of this Paper.

        The version of the paper.  # noqa: E501

        :param version: The version of this Paper.
        :type version: str
        """

        self._version = version

    @property
    def source(self) -> str:
        """Gets the source of this Paper.

        The source of the paper. Either \"bioRxiv\" or \"medRxiv\".  # noqa: E501

        :return: The source of this Paper.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source: str):
        """Sets the source of this Paper.

        The source of the paper. Either \"bioRxiv\" or \"medRxiv\".  # noqa: E501

        :param source: The source of this Paper.
        :type source: str
        """

        self._source = source

    @property
    def journal(self) -> str:
        """Gets the journal of this Paper.

        The journal the paper was published in.  # noqa: E501

        :return: The journal of this Paper.
        :rtype: str
        """
        return self._journal

    @journal.setter
    def journal(self, journal: str):
        """Sets the journal of this Paper.

        The journal the paper was published in.  # noqa: E501

        :param journal: The journal of this Paper.
        :type journal: str
        """

        self._journal = journal

    @property
    def title(self) -> str:
        """Gets the title of this Paper.


        :return: The title of this Paper.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this Paper.


        :param title: The title of this Paper.
        :type title: str
        """

        self._title = title

    @property
    def abstract(self) -> str:
        """Gets the abstract of this Paper.


        :return: The abstract of this Paper.
        :rtype: str
        """
        return self._abstract

    @abstract.setter
    def abstract(self, abstract: str):
        """Sets the abstract of this Paper.


        :param abstract: The abstract of this Paper.
        :type abstract: str
        """

        self._abstract = abstract

    @property
    def journal_doi(self) -> str:
        """Gets the journal_doi of this Paper.


        :return: The journal_doi of this Paper.
        :rtype: str
        """
        return self._journal_doi

    @journal_doi.setter
    def journal_doi(self, journal_doi: str):
        """Sets the journal_doi of this Paper.


        :param journal_doi: The journal_doi of this Paper.
        :type journal_doi: str
        """

        self._journal_doi = journal_doi

    @property
    def published_journal_title(self) -> str:
        """Gets the published_journal_title of this Paper.


        :return: The published_journal_title of this Paper.
        :rtype: str
        """
        return self._published_journal_title

    @published_journal_title.setter
    def published_journal_title(self, published_journal_title: str):
        """Sets the published_journal_title of this Paper.


        :param published_journal_title: The published_journal_title of this Paper.
        :type published_journal_title: str
        """

        self._published_journal_title = published_journal_title

    @property
    def pub_date(self) -> datetime:
        """Gets the pub_date of this Paper.


        :return: The pub_date of this Paper.
        :rtype: datetime
        """
        return self._pub_date

    @pub_date.setter
    def pub_date(self, pub_date: datetime):
        """Sets the pub_date of this Paper.


        :param pub_date: The pub_date of this Paper.
        :type pub_date: datetime
        """

        self._pub_date = pub_date

    @property
    def authors(self) -> List[Author]:
        """Gets the authors of this Paper.


        :return: The authors of this Paper.
        :rtype: List[Author]
        """
        return self._authors

    @authors.setter
    def authors(self, authors: List[Author]):
        """Sets the authors of this Paper.


        :param authors: The authors of this Paper.
        :type authors: List[Author]
        """

        self._authors = authors

    @property
    def revdate(self) -> datetime:
        """Gets the revdate of this Paper.


        :return: The revdate of this Paper.
        :rtype: datetime
        """
        return self._revdate

    @revdate.setter
    def revdate(self, revdate: datetime):
        """Sets the revdate of this Paper.


        :param revdate: The revdate of this Paper.
        :type revdate: datetime
        """

        self._revdate = revdate

    @property
    def entities(self) -> List[str]:
        """Gets the entities of this Paper.


        :return: The entities of this Paper.
        :rtype: List[str]
        """
        return self._entities

    @entities.setter
    def entities(self, entities: List[str]):
        """Sets the entities of this Paper.


        :param entities: The entities of this Paper.
        :type entities: List[str]
        """

        self._entities = entities

    @property
    def assays(self) -> List[str]:
        """Gets the assays of this Paper.


        :return: The assays of this Paper.
        :rtype: List[str]
        """
        return self._assays

    @assays.setter
    def assays(self, assays: List[str]):
        """Sets the assays of this Paper.


        :param assays: The assays of this Paper.
        :type assays: List[str]
        """

        self._assays = assays

    @property
    def main_topics(self) -> List[List[str]]:
        """Gets the main_topics of this Paper.


        :return: The main_topics of this Paper.
        :rtype: List[List[str]]
        """
        return self._main_topics

    @main_topics.setter
    def main_topics(self, main_topics: List[List[str]]):
        """Sets the main_topics of this Paper.


        :param main_topics: The main_topics of this Paper.
        :type main_topics: List[List[str]]
        """

        self._main_topics = main_topics

    @property
    def highlighted_entities(self) -> List[str]:
        """Gets the highlighted_entities of this Paper.


        :return: The highlighted_entities of this Paper.
        :rtype: List[str]
        """
        return self._highlighted_entities

    @highlighted_entities.setter
    def highlighted_entities(self, highlighted_entities: List[str]):
        """Sets the highlighted_entities of this Paper.


        :param highlighted_entities: The highlighted_entities of this Paper.
        :type highlighted_entities: List[str]
        """

        self._highlighted_entities = highlighted_entities

    @property
    def slug(self) -> str:
        """Gets the slug of this Paper.


        :return: The slug of this Paper.
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, slug: str):
        """Sets the slug of this Paper.


        :param slug: The slug of this Paper.
        :type slug: str
        """

        self._slug = slug

    @property
    def reviewed_by(self) -> List[str]:
        """Gets the reviewed_by of this Paper.


        :return: The reviewed_by of this Paper.
        :rtype: List[str]
        """
        return self._reviewed_by

    @reviewed_by.setter
    def reviewed_by(self, reviewed_by: List[str]):
        """Sets the reviewed_by of this Paper.


        :param reviewed_by: The reviewed_by of this Paper.
        :type reviewed_by: List[str]
        """

        self._reviewed_by = reviewed_by