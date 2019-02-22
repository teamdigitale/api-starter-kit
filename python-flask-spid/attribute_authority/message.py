#
# Process claims && co.
#
from time import time
from uuid import uuid4

import jwt

ENCRYPTION_KEY = "secret"

# private_key = b'-----BEGIN PRIVATE KEY-----\nMIGEAgEAMBAGByqGSM49AgEGBS...'
# public_key = b'-----BEGIN PUBLIC KEY-----\nMHYwEAYHKoZIzj0CAQYFK4EEAC...'
# encoded = jwt.encode({'some': 'payload'}, private_key, algorithm='RS256')
# decoded = jwt.decode(encoded, public_key, algorithms='RS256')


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


def sign_token(token):
    return jwt.encode(token, ENCRYPTION_KEY, "HS256")


def validate_token(content):
    content = content
    return jwt.decode(content, ENCRYPTION_KEY, audience="ipa/oou", algorithms=["HS256"])
