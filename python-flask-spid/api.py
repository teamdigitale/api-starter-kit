import datetime
from os.path import join as pjoin

from decorator import decorator

from connexion import problem
from flask import current_app as app
from flask import make_response, redirect, render_template, request, session
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
    return problem(status=200, title="Success", detail="Application is up", ext={"result": "ok"})


def index():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req, app.config)
    errors = []
    return {
        "message": "Welcome to the Jungle 1",
        "_links": [
            {"url": pjoin(request.url_root, "echo")}
        ]
    }
