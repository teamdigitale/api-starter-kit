#
# run me with nosetests -vs test_oas.py
#
import logging
import sys

import connexion
from flask_testing import TestCase

from attribute_authority.message import create_token, sign_token, validate_token
from util import FakeResolver

me = sys.modules[__name__]


def noop(*args, **kwds):
    raise NotImplementedError


class BaseTestCase(TestCase):
    def create_app(self):
        logging.getLogger("connexion.operation").setLevel("ERROR")
        app = connexion.App(__name__, specification_dir=".")
        app.add_api("../attribute_authority/attribute-authority.yaml")
        return app.app


def test_oas3():
    files = ("../attribute_authority/attribute-authority.yaml",)

    def assert_parse_oas3(zapp, f):
        zapp.add_api(f, resolver=FakeResolver(me))

    for f in files:
        zapp = connexion.FlaskApp(__name__, specification_dir=".")
        yield assert_parse_oas3, zapp, f


class TestPublicController(BaseTestCase):
    """PublicController integration test stubs"""

    def harn_post(self, taxCode, data):
        return self.client.open(
            "/aa/v1/attribute/driving_license/" + taxCode,
            headers={"Content-Type": "application/jose", "Accept": "application/json"},
            method="POST",
            data=sign_token(data),
        )

    def test_decode_jose(self):
        """Test case for get_echo
        """
        data = create_token({"v": "0.0.1", "attributes": ["driving_license"]})
        response = self.harn_post('MRORSS77T05E472I', data)
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))
        try:
            validate_token(response.data.decode("utf-8"))
        except Exception as e:
            raise ValueError(e, response.data)

    def test_get_status_unauthenticated(self):
        """Test case for get_metadata
        """
        response = self.client.open("/aa/v1/status", method="GET")
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))
