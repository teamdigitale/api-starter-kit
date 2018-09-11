import datetime
from os.path import join as pjoin

from connexion import problem
from decorator import decorator
from flask import current_app as app
from flask import make_response, redirect, render_template, request, session

from spid import init_saml_auth, prepare_flask_request


@decorator
def is_authenticated(f, *args, **kwargs):
    if 'samlUserdata' not in session:
        login_url = pjoin(request.url_root, "saml?sso")
        return problem(status=401, title="Unauthorized", detail=[{"href": login_url}])
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


def get_config():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req, app.config)
    return auth.get_settings().get_idp_data()


def get_metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req, app.config)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if not errors:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp
