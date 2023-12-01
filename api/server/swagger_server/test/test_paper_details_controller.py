# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.paper_sort_by import PaperSortBy  # noqa: E501
from swagger_server.models.sort_order import SortOrder  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPaperDetailsController(BaseTestCase):
    """PaperDetailsController integration test stubs"""

    def test_papers_get(self):
        """Test case for papers_get

        Get paginated collections of papers, optionally filtered by reviewing service
        """
        query_string = [('reviewed_by', 'reviewed_by_example'),
                        ('query', 'query_example'),
                        ('page', 2),
                        ('per_page', 100),
                        ('sort_by', PaperSortBy()),
                        ('sort_order', SortOrder())]
        response = self.client.open(
            '/api/v2/papers/',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
