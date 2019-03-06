#
# run me with nosetests -vs test_aa.py
#
import logging
import sys

import connexion
from flask_testing import TestCase

from attribute_authority.crypto import init_certs
from attribute_authority.message import (
    create_token,
    pem_to_x5c,
    sign_token,
    validate_token,
)
from util import FakeResolver

me = sys.modules[__name__]


def noop(*args, **kwds):
    raise NotImplementedError


class BaseTestCase(TestCase):
    def create_app(self):
        logging.getLogger("connexion.operation").setLevel("ERROR")
        app = connexion.App(__name__, specification_dir=".")
        app.add_api("../attribute_authority/attribute-authority.yaml")
        self.dummy_config = init_certs()
        app.app.config.update(self.dummy_config)

        self.public_cert = open(self.dummy_config["https_cert_file"]).read()
        self.private_key = open(self.dummy_config["https_key_file"]).read()
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

    def harn_post(self, path, taxCode, data):

        signed = sign_token(
            data,
            key=self.private_key,
            headers={
                "typ": "JWT",
                "alg": "ES256",
                "x5c": [pem_to_x5c(self.public_cert)],
            },
        )
        print("signed_token" + signed)
        return self.client.open(
            path % taxCode,
            headers={
                "Content-Type": "application/jose",
                "Accept": "application/json",
            },
            method="POST",
            data=signed,
        )

    def test_parse_and_validate_response_jose(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["driving_license"]}
        )
        token["aud"] = self.dummy_config["entityId"]
        response = self.harn_post(
            "/aa/v1/attributes/driving_license/%s", "MRORSS77T05E472I", token
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )
        try:
            validate_token(response.data.decode("utf-8"))
        except Exception as e:
            raise ValueError(e, response.data)

    def test_invalid_jose_400(self):
        data = create_token({"v": "0.0.1", "attributes": ["driving_license"]})
        data["aud"] = "INVALID"
        response = self.harn_post(
            "/aa/v1/attributes/driving_license/%s", "MRORSS77T05E472I", data
        )
        self.assert400(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_get_status_unauthenticated(self):
        response = self.client.open("/aa/v1/status", method="GET")
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_get_metadata(self):
        response = self.client.open("/aa/v1/metadata", method="GET")
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )
        assert "entityId" in response.json

    def test_missing_consent(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["invalido_di_guerra"]}
        )
        token["aud"] = self.dummy_config["entityId"]
        response = self.harn_post(
            "/aa/v1/consent-attributes/invalido_di_guerra/%s",
            "MRORSS77T05E472I",
            token,
        )
        self.assert403(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_post_consent(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["invalido_di_guerra"]}
        )
        token["aud"] = self.dummy_config["entityId"]
        response = self.harn_post(
            "/aa/v1/consents/%s?callback_url=https://foo",
            "XKFLNX28D67Q295Q",
            token,
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

        assert "detail" in response.json

    def test_with_consent(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["invalido_di_guerra"]}
        )
        token["aud"] = self.dummy_config["entityId"]
        # set consent.
        response = self.harn_post(
            "/aa/v1/consents/%s?callback_url=foo&consent=bar",
            "MRORSS77T05E472I",
            token,
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )
        #
        response = self.harn_post(
            "/aa/v1/consent-attributes/invalido_di_guerra/%s",
            "MRORSS77T05E472I",
            token,
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )

    def test_get_consent_menu(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["invalido_di_guerra"]}
        )
        token["aud"] = self.dummy_config["entityId"]

        signed = sign_token(
            token,
            key=self.private_key,
            headers={
                "typ": "JWT",
                "alg": "ES256",
                "x5c": [pem_to_x5c(self.public_cert)],
            },
        )

        response = self.client.open(
            "/aa/v1/consents/%s?callback_url=foo&consent={signed}".format(
                signed=signed
            )
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )
        assert response.json["token"]["attributes"]

    def test_get_consent_accept(self):
        token = create_token(
            {"v": "0.0.1", "attributes": ["invalido_di_guerra"]}
        )
        token["aud"] = self.dummy_config["entityId"]

        signed = sign_token(
            token,
            key=self.private_key,
            headers={
                "typ": "JWT",
                "alg": "ES256",
                "x5c": [pem_to_x5c(self.public_cert)],
            },
        )

        response = self.client.open(
            "/aa/v1/consents/%s?callback_url=foo&consent={signed}&accept=yes".format(
                signed=signed
            )
        )
        self.assert200(
            response, "Response body is : " + response.data.decode("utf-8")
        )
        assert response.json["token"]["attributes"]
