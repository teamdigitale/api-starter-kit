#
# Process claims && co.
#
import binascii
from base64 import decodestring
from time import time
from uuid import uuid4

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (Encoding,
                                                          load_der_private_key,
                                                          load_pem_private_key)
from cryptography.x509 import (load_der_x509_certificate,
                               load_pem_x509_certificate)

ENCRYPTION_KEY = "secret"


def create_token(base):
    ts = int(time())
    base = base or {}

    return dict(
        base,
        **{
            "iss": "ipa/oou",
            "aud": "ipa/oou",
            "sub": "the message id",
            "nbf": ts - 2,
            "iat": ts,
            "exp": ts + 2000,
            "jti": str(uuid4()),
            "b_hash": "my-body-hash",
        }
    )


def x5c_to_x509(x5c):
    return load_der_x509_certificate(decodestring(x5c), default_backend())


def pem_to_x509(x509_pem):
    return load_pem_x509_certificate(x509_pem, default_backend())


def pem_to_x5c(x509_pem):
    if is_pem(x509_pem):
        return ''.join(x509_pem.strip().split("\n")[1:-1])
    raise ValueError("Not a PEM certificate")


def x509_to_pem(x509):
    return x509.public_bytes(Encoding.PEM)


def is_pem(key_or_certificate):
    return key_or_certificate.startswith("-----")


def is_x5c(key_or_certificate):
    try:
        decodestring(key_or_certificate)
    except binascii.Error:
        return False
    return key_or_certificate.startswith('MI')


def sign_request(token, app_config=None, alg="ES256"):
    """Sign a request taking the private key from app_config
        and adding the x5c header with the certificate.

    :param token:
    :param app_config:
    :param alg:
    :return:
    """
    if is_pem(app_config['x509cert']):
        x5c = pem_to_x5c(app_config['x509cert'])
    elif is_x5c(app_config['x509cert']):
        x5c = app_config['x509cert']
    else:
        raise ValueError("Not an embeddable certificate: %s" %
                         app_config['x509cert'])

    return sign_token(
        token,
        key=app_config['privateKey'],
        alg=alg,
        headers={"typ": "JWT", "alg": alg,
                 "x5c": [x5c]},
    )


def validate_request(token, app_config=None, alg="ES256"):
    audience = app_config["entityId"]
    return validate_token(
        token,
        audience=audience,
        alg=alg
    )


def sign_token(token, key=None, alg="ES256", **kwargs):
    """Sign a token.

    :param token:
    :param key:
    :param alg:
    :param kwargs:
    :return:
    """
    if 'alg' in kwargs.get('headers', {}):
        assert kwargs['headers']['alg'] == alg
    if is_pem(key):
        key = load_pem_private_key(
            key, password=None, backend=default_backend())
    elif is_x5c(key):
        key = load_der_private_key(decodestring(
            key), password=None, backend=default_backend())

    print("key: %s, alg: %s" % (key, alg))
    return jwt.encode(token, key, alg, **kwargs)


def validate_token(content, audience="ipa/oou", key=None, alg="ES256", **kwargs):

    # If no key is provided, check x5c.
    if not key:
        try:
            jwh = jwt.get_unverified_header(content)
            x5c_pem = jwh['x5c'][0]
            alg = jwh['alg']
        except (KeyError, IndexError):
            x5c_pem = None

        if x5c_pem:
            key = x5c_to_x509(x5c_pem).public_key()
    elif key.startswith("-" * 5):
        key = pem_to_x509(key).public_key()

    return jwt.decode(content, key, audience=audience, algorithms=[alg], **kwargs)
