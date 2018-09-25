import datetime
from os.path import join as pjoin
from random import randint

from connexion import problem
from decorator import decorator
from flask import current_app as app
from flask import request, session
from spid import init_saml_auth, prepare_flask_request


@decorator
def is_authenticated(f, *args, **kwargs):
    if 'samlUserdata' not in session:
        login_url = pjoin(request.url_root, "saml?sso")
        return problem(status=401,
                       title="Unauthorized",
                       detail="User not authenticated",
                       instance=request.url,
                       headers={
                           'foo': 'bar'
                       },
                       ext={
                           "_links": [
                               {"href": login_url}
                           ]
                       })
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
    attributes = session['samlUserdata'].items()
    return dict(attributes)


def get_status():
    """Ritorna lo stato dell'applicazione.

    Ritorna lo stato dell'applicazione.  # noqa: E501


    :rtype: Problem
    """
    p = randint(0, 10)

    if p < 7:
        return problem(status=200, title="Success",
                       detail="Il servizio funziona correttamente",
                       ext={"result": "ok"},
                       headers={
                           'Cache-control': 'no-cache'
                       })
    if p < 9:
        return problem(status=503, title="Service Unavailable",
                       detail="Questo errore viene ritornato randomicamente.",
                       headers={
                           'Retry-After': '1',
                           'Cache-control': 'no-cache'
                       })

    return problem(status=429, title="Too Many Requests",
                   detail="Questo errore viene ritornato randomicamente.",
                   headers={
                       'Cache-control': 'no-cache',
                       'X-RateLimit-Limit': '10',
                       'X-RateLimit-Reset': '1',
                       'X-RateLimit-Remaining': '0',
                       'Retry-After': '1',
                   })


def index():
    req = prepare_flask_request(request)
    init_saml_auth(req, app.config)
    return {
        "message": "Welcome to the Jungle 1",
        "_links": [
            {"url": pjoin(request.url_root, "echo")}
        ]
    }
