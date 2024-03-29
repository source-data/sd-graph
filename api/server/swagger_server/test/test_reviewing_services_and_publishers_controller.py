# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.publisher_description import PublisherDescription  # noqa: E501
from swagger_server.models.reviewing_service_description import ReviewingServiceDescription  # noqa: E501
from swagger_server.test import BaseTestCase


class TestReviewingServicesAndPublishersController(BaseTestCase):
    """ReviewingServicesAndPublishersController integration test stubs"""

    def test_publishers_get(self):
        """Test case for publishers_get

        Get information about available publishers.
        """
        response = self.client.open(
            '/api/v2/publishers/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_reviewing_services_get(self):
        """Test case for reviewing_services_get

        Get information about available reviewing services.
        """
        response = self.client.open(
            '/api/v2/reviewing_services/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
