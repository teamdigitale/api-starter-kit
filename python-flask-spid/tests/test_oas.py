#
# run me with nosetests -vs test_oas.py
#
import logging
import sys

import connexion
from flask_testing import TestCase

from util import FakeResolver

me = sys.modules[__name__]


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger("connexion.operation").setLevel("ERROR")
        app = connexion.App(__name__, specification_dir=".")
        app.add_api("../spid.yaml")
        app.app.config["SAML_PATH"] = "../saml/"
        return app.app


def test_oas3():
    files = ("spid.yaml",)

    def assert_parse_oas3(zapp, f):
        zapp.add_api(f, resolver=FakeResolver())

    for f in files:
        zapp = connexion.FlaskApp(__name__, specification_dir=".")
        yield assert_parse_oas3, zapp, f


class TestPublicController(BaseTestCase):
    """PublicController integration test stubs"""

    def test_get_echo_401(self):
        """Test case for get_echo
        """
        response = self.client.open("/echo", method="GET")
        self.assert401(response, "Response body is : " +
                       response.data.decode("utf-8"))

    def test_get_metadata_unauthenticated(self):
        """Test case for get_metadata
        """
        response = self.client.open("/metadata", method="GET")
        self.assert200(response, "Response body is : " +
                       response.data.decode("utf-8"))
