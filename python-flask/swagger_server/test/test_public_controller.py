# coding: utf-8

from __future__ import absolute_import

from swagger_server.test import BaseTestCase


class TestPublicController(BaseTestCase):
    """PublicController integration test stubs"""

    def test_get_echo(self):
        """Test case for get_echo

        Ritorna un timestamp in formato RFC5424.
        """
        response = self.client.open(
            '/datetime/v1/echo',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
