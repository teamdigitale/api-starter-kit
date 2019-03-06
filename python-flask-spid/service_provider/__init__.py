import datetime
from os.path import join as pjoin
from random import randint
from socket import gethostbyname

from connexion import problem
from decorator import decorator
from flask import current_app as app
from flask import request, session
from spid import init_saml_auth, prepare_flask_request
from requests import post
from attribute_authority.message import (
    create_token,
    sign_request,
    validate_request,
)
from attribute_authority.errors import invalid_token_handler
import jwt


@decorator
def is_authenticated(f, *args, **kwargs):
    if "samlUserdata" not in session:
        login_url = pjoin(request.url_root, "saml?sso")
        return problem(
            status=401,
            title="Unauthorized",
            detail="User not authenticated",
            instance=request.url,
            headers={"foo": "bar"},
            ext={"_links": [{"href": login_url}]},
        )
    return f(*args, **kwargs)


@is_authenticated
def get_echo():  # noqa: E501
    """Ritorna un timestamp in formato RFC5424.

    Ritorna un timestamp in formato RFC5424 prendendola dal server attuale.  # noqa: E501


    :rtype: Timestampa
    """
    return {"datetime": str(datetime.datetime.utcnow())}


@is_authenticated
def get_attrs():
    attributes = session["samlUserdata"].items()
    return dict(attributes)


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


@is_authenticated
def get_attribute_simple(attribute="driving_license"):
    taxCode = "".join(session["samlUserdata"]["fiscalNumber"])
    AA_URL = pjoin("https://aa/aa/v1/attributes/", attribute, taxCode)
    gethostbyname("aa")
    token = create_token({"v": "0.0.1", "attributes": [attribute]})
    token["iss"] = app.config["entityId"]
    token["aud"] = "https://%s/aa/v1/metadata" % gethostbyname("aa")
    token = sign_request(token, app_config=app.config, alg="RS256")

    ret = post(
        AA_URL,
        data=token,
        verify=False,
        headers={"content-type": "application/jose"},
    )
    if ret.status_code != 200:
        app.logger.error(ret.content)
        aa_problem = problem(
            instance=AA_URL,
            status=ret.status_code,
            title="errore della AA",
            detail=ret.content,
        )
        return aa_problem

    try:
        attributes = validate_request(
            ret.content.decode("utf8"), alg="ES256", app_config=app.config
        )
    except jwt.exceptions.InvalidTokenError as e:
        return invalid_token_handler(e)
    except Exception as e:
        raise ValueError(e, request.data)

    return attributes


@is_authenticated
def get_attribute_consent(attribute="invalido_di_guerra"):
    taxCode = "".join(session["samlUserdata"]["fiscalNumber"])
    AA_URL = pjoin("https://aa/aa/v1/consent-attributes/", attribute, taxCode)
    token = create_token({"v": "0.0.1", "attributes": [attribute]})
    token["iss"] = app.config["entityId"]
    token["aud"] = "https://%s/aa/v1/metadata" % gethostbyname("aa")
    token = sign_request(token, app_config=app.config, alg="RS256")

    ret = post(
        AA_URL,
        data=token,
        verify=False,
        headers={"content-type": "application/jose"},
    )

    if ret.status_code == 403:
        return go_to_get_consent(
            taxCode, callback_url=request.url, consent=token
        )

    if ret.status_code != 200:
        app.logger.error(ret.content)
        aa_problem = problem(
            instance=AA_URL,
            status=ret.status_code,
            title="errore della AA",
            detail=ret.content,
        )
        return aa_problem

    try:
        attributes = validate_request(
            ret.content.decode("utf8"), alg="ES256", app_config=app.config
        )
    except jwt.exceptions.InvalidTokenError as e:
        return invalid_token_handler(e)
    except Exception as e:
        raise ValueError(e, request.data)

    return attributes


def go_to_get_consent(taxCode, callback_url=None, consent=None):
    # TODO simple implementation of getting consent via a GET
    # instead of a POST with token.
    return {
        "_link": [
            {
                "description": "You should go and get consent to the following link",
                "url": (
                    "https://{aa_host}/aa/v1/consents/{taxCode}?"
                    "callback_url={callback_url}"
                    "&consent={consent}"
                ).format(
                    aa_host=gethostbyname("aa"),
                    taxCode=taxCode,
                    callback_url=callback_url,
                    consent=consent,
                ),
            }
        ]
    }


def index():
    req = prepare_flask_request(request)
    init_saml_auth(req, app.config)
    return {
        "message": "Welcome to the Jungle 1",
        "_links": [
            {"url": pjoin(request.url_root, "echo")},
            {
                "url": pjoin(request.url_root, "my-attributes"),
                "description": "Show all user idp-attributes.",
            },
            {
                "url": pjoin(
                    request.url_root, "aa/attributes/driving_license"
                ),
                "description": "Show driving license from Attribute Authority",
            },
        ],
    }
