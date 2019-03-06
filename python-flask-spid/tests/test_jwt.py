from attribute_authority.crypto import mkcert
from attribute_authority.message import pem_to_x5c, sign_token, validate_token


def setup():
    mkcert("/tmp/1.key", "/tmp/1.pem", "localhost", "sample")


def test_sign_verify():
    private_key = open("/tmp/1.key", "r").read()
    public_key = open("/tmp/1.pem", "r").read()

    token = sign_token(
        {"aud": "ipa/oou"},
        key=private_key,
        headers={"typ": "JWT", "alg": "ES256"},
    )
    validate_token(token, audience="ipa/oou", key=public_key)


def test_sign_verify_x5c():
    private_key = open("/tmp/1.key", "r").read()
    public_pem = open("/tmp/1.pem", "r").read()

    token = sign_token(
        {"aud": "ipa/oou"},
        key=private_key,
        headers={
            "typ": "JWT",
            "alg": "ES256",
            "x5c": [pem_to_x5c(public_pem)],
        },
    )
    validate_token(token, audience="ipa/oou")


def test_sign_verify_noaud():
    private_key = open("/tmp/1.key", "r").read()
    public_pem = open("/tmp/1.pem", "r").read()

    token = sign_token(
        {"aud": "ipa/oou"},
        key=private_key,
        headers={"typ": "JWT", "alg": "ES256"},
    )
    validate_token(token, key=public_pem)
