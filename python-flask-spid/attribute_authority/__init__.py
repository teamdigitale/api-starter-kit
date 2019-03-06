from os.path import join as pjoin
from random import randint
from time import time

from connexion import problem
from flask import Response
from flask import request
from flask import current_app as app
import jwt
from datetime import datetime

# from api import is_authenticated
from message import create_token, sign_request, validate_token
from errors import invalid_token_handler

AA_URL = "https://localhost/"

MOCK_DB = {
    "MRORSS77T05E472I": {
        "driving_license": "UX1234567",
        "invalido_di_guerra": True,
        "consent": 0,
    },
    "XKFLNX28D67Q295Q": {
        "driving_license": "UX1234567",
        "invalido_di_guerra": True,
        "consent": 0,
    },
}


def _get_user_data(taxCode):
    if set(taxCode) == {"0", "Z"}:
        return None
    _, user_data = next(iter(MOCK_DB.items()))
    return user_data


def get_attribute_simple(taxCode):
    """
    Return
    :param taxCode:
    :return:
    """
    content_type = request.headers.get("Content-Type", "")
    assert content_type.lower() == "application/jose"

    user_data = _get_user_data(taxCode)
    if not user_data:
        return problem(
            title="User Not Found", status=404, detail="Missing user"
        )

    try:
        claims = validate_token(request.data, audience=app.config["entityId"])
    except jwt.exceptions.InvalidTokenError as e:
        return invalid_token_handler(e)
    except Exception as e:
        raise ValueError(e, request.data)

    assert claims["v"] == "0.0.1", claims
    assert claims["attributes"], claims

    aa = [
        {"attribute": a, "value": user_data[a]}
        for a in claims["attributes"]
        if a in user_data
    ]

    token = create_token({"v": "0.0.1", "attributes": aa})
    token["iss"] = app.config["entityId"]
    token["aud"] = claims["iss"]

    signed_token = sign_request(token, app_config=app.config)

    return Response(
        response=signed_token, status=200, mimetype="application/jose"
    )


def get_attribute_consent(taxCode):
    """Receives a token and asks for permission if
       required.
    Return
    :param taxCode:
    :return:
    """
    content_type = request.headers.get("Content-Type", "")
    assert content_type.lower() == "application/jose"

    user_data = _get_user_data(taxCode)
    if not user_data:
        return problem(
            title="User Not Found", status=404, detail="Missing user"
        )

    try:
        claims = validate_token(request.data, audience=app.config["entityId"])
    except jwt.exceptions.InvalidTokenError as e:
        return invalid_token_handler(e)
    except Exception as e:
        raise ValueError(e, request.data)

    assert claims["v"] == "0.0.1", claims
    assert claims["attributes"], claims

    if user_data["consent"] + 30 < time():
        return problem(
            status=403,
            title="ConsentRequired",
            detail="User consent is required for this attribute. Last given: %r"
            % datetime.fromtimestamp(user_data["consent"]),
            type="https://spid.gov.it/aa/problem/consent-required",
            ext={"consent_url": "https://aa/v1/consents/{taxCode}/"},
        )

    aa = [
        {"attribute": a, "value": user_data[a]}
        for a in claims["attributes"]
        if a in user_data
    ]

    token = create_token({"v": "0.0.1", "attributes": aa})
    token["iss"] = app.config["entityId"]
    token["aud"] = claims["iss"]

    signed_token = sign_request(token, app_config=app.config)

    return Response(
        response=signed_token, status=200, mimetype="application/jose"
    )


def post_consent(taxCode, callback_url):
    content_type = request.headers.get("Content-Type", "")
    assert content_type.lower() == "application/jose"

    user_data = _get_user_data(taxCode)
    if not user_data:
        return problem(
            title="User Not Found", status=404, detail="Missing user"
        )

    user_data["consent"] = time()

    return problem(
        title="OK",
        status=200,
        detail="Consent given until %r"
        % datetime.fromtimestamp(user_data["consent"]),
        ext={"_link": [{"url": callback_url}]},
    )


def get_consent(taxCode, callback_url, consent, accept=False):
    user_data = _get_user_data(taxCode)
    if not user_data:
        return problem(
            title="User Not Found", status=404, detail="Missing user"
        )

    if not accept:
        token = validate_token(
            consent, valid=False, audience=app.config["entityId"]
        )
        return problem(
            title="OK",
            status=200,
            detail="Do you want to give access to %r for the following jwt"
            % token["iss"],
            ext={
                "_link": [{"url": request.url + "&accept=yes"}],
                "callback_url": callback_url,
                "token": token,
            },
        )

    user_data["consent"] = time()

    return problem(
        title="Redirecting to consent",
        status=302,
        detail="Redirecto to POST",
        headers={"Location": callback_url},
    )
    raise NotImplementedError


def get_metadata():
    return {
        "x509cert": open(app.config["https_cert_file"])
        .read()
        .replace("\n", ""),
        "entityId": app.config["entityId"],
    }


def get_status():
    """Ritorna lo stato dell'applicazione.

    Ritorna lo stato dell'applicazione.  # noqa: E501


    :rtype: Problem
    """
    p = randint(0, 10)

    if p < 7:
        return problem(
            status=200,
            title="Success",
            detail="Il servizio funziona correttamente",
            ext={"result": "ok"},
            headers={"Cache-control": "no-cache"},
        )
    if p < 9:
        return problem(
            status=503,
            title="Service Unavailable",
            detail="Questo errore viene ritornato randomicamente.",
            headers={"Retry-After": "1", "Cache-control": "no-cache"},
        )

    return problem(
        status=429,
        title="Too Many Requests",
        detail="Questo errore viene ritornato randomicamente.",
        headers={
            "Cache-control": "no-cache",
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Reset": "1",
            "X-RateLimit-Remaining": "0",
            "Retry-After": "1",
        },
    )


def index():
    return {
        "_links": [
            {
                "url": pjoin(
                    request.url_root,
                    "attribute/driving_license/MRRRSS77T05E472I",
                )
            },
            {"url": pjoin(request.url_root, "metadata")},
        ]
    }
