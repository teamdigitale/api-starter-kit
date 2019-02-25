from os.path import join as pjoin
from random import randint

from connexion import problem
from flask import Response
from flask import request
from flask import current_app as app
import jwt

# from api import is_authenticated
from message import create_token, sign_request, validate_token
from errors import invalid_token_handler

AA_URL = "https://localhost/"

MOCK_DB = {
    "MRORSS77T05E472I": {"driving_license": "UX1234567"},
    "XKFLNX28D67Q295Q": {"driving_license": "UX1234567"},
}


def get_attribute_simple(taxCode):
    """
    Return
    :param taxCode:
    :return:
    """
    content_type = request.headers.get("Content-Type", "")
    assert content_type.lower() == "application/jose"

    user_data = MOCK_DB.get(taxCode)
    if not user_data:
        return problem(title="User Not Found", status=404, detail="Missing user")

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

    signed_token = sign_request(
        token,
        app_config=app.config
    )

    return Response(
        response=signed_token, status=200, mimetype="application/jose"
    )


def get_attribute_complex(taxCode):
    raise NotImplementedError


def get_metadata():
    return {
        "x509cert": open(app.config["https_cert_file"]).read().replace("\n", ""),
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
            {"url": pjoin(
                request.url_root, "attribute/driving_license/MRRRSS77T05E472I"
            )},
            {"url": pjoin(request.url_root, "metadata")}
        ]
    }
