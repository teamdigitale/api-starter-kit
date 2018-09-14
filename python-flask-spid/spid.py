import logging
import socket
from base64 import b64encode
from os.path import join as pjoin

from lxml.etree import parse
from requests import get
from six import StringIO
from six.moves.urllib.parse import urlparse

from connexion import problem
from flask import current_app as app
from flask import make_response, redirect, render_template, request, session
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

logging.basicConfig(level=logging.DEBUG)
root = logging.getLogger()


class SpidAuthnRequest(object):
    """

    This class handles an AuthNRequest. It builds an
    AuthNRequest object.

    """

    def __init__(self, settings, force_authn=False, is_passive=False, set_nameid_policy=True):
        """
        Constructs the AuthnRequest object.

        :param settings: OSetting data
        :type return_to: OneLogin_Saml2_Settings

        :param force_authn: Optional argument. When true the AuthNRequest will set the ForceAuthn='true'.
        :type force_authn: bool

        :param is_passive: Optional argument. When true the AuthNRequest will set the Ispassive='true'.
        :type is_passive: bool

        :param set_nameid_policy: Optional argument. When true the AuthNRequest will set a nameIdPolicy element.
        :type set_nameid_policy: bool
        """
        self.__settings = settings

        sp_data = self.__settings.get_sp_data()
        idp_data = self.__settings.get_idp_data()
        security = self.__settings.get_security_data()

        uid = OneLogin_Saml2_Utils.generate_unique_id()
        self.__id = uid
        issue_instant = OneLogin_Saml2_Utils.parse_time_to_SAML(
            OneLogin_Saml2_Utils.now())

        destination = idp_data['singleSignOnService']['url']

        provider_name_str = ''
        organization_data = settings.get_organization()
        if isinstance(organization_data, dict) and organization_data:
            langs = organization_data.keys()
            lang = 'en-US' if 'en-US' in langs else langs[0]
            if organization_data[lang].get('displayname') is not None:
                # SPID ignores this parameter
                pass

        force_authn_str = '\n    ForceAuthn="true"' if force_authn is True else ""
        is_passive_str = '\n    IsPassive="true"' if is_passive is True else ''

        nameid_policy_str = ''
        if set_nameid_policy:
            name_id_policy_format = sp_data['NameIDFormat']
            if security.get('wantNameIdEncrypted'):
                name_id_policy_format = OneLogin_Saml2_Constants.NAMEID_ENCRYPTED

            nameid_policy_str = """<samlp:NameIDPolicy Format="%s" />""" % name_id_policy_format

        requested_authn_context_str = ''
        if security.get('requestedAuthnContext', False) is not False:
            authn_comparison = 'exact'
            if 'requestedAuthnContextComparison' in security:
                authn_comparison = security['requestedAuthnContextComparison']

            if security['requestedAuthnContext'] is True:
                requested_authn_context_str = """
                <samlp:RequestedAuthnContext Comparison="{authn_comparison}">
                    <saml:AuthnContextClassRef>{spid_level}</saml:AuthnContextClassRef>
                </samlp:RequestedAuthnContext>""".format(
                    authn_comparison=authn_comparison,
                    spid_level="https://www.spid.gov.it/SpidL2")
            else:
                attrlist = '\n'.join([
                    '<saml:AuthnContextClassRef>{authn_context}</saml:AuthnContextClassRef>'.format(
                        authn_context=authn_context
                    )
                    for authn_context
                    in security['requestedAuthnContext']
                ])
                requested_authn_context_str = (
                    '<samlp:RequestedAuthnContext Comparison="{authn_comparison}">'
                    '{attrlist}'
                    '</samlp:RequestedAuthnContext>').format(
                    authn_comparison=authn_comparison, attrlist=attrlist
                )

        attr_consuming_service_str = 'AttributeConsumingServiceIndex="1"' if sp_data.get(
            'attributeConsumingService') else ""

        request = (
            """<samlp:AuthnRequest
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="%(id)s"
            Version="2.0"%(provider_name)s%(force_authn_str)s%(is_passive_str)s
            IssueInstant="%(issue_instant)s"
            Destination="%(destination)s"
            ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            AssertionConsumerServiceURL="%(assertion_url)s"
            %(attr_consuming_service_str)s>"""
            """<saml:Issuer 
                Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity"
                NameQualifier="%(entity_id)s"
                >%(entity_id)s</saml:Issuer>%(nameid_policy_str)s%(requested_authn_context_str)s
            </samlp:AuthnRequest>""") % \
            {
                'id': uid,
                'provider_name': provider_name_str,
                'force_authn_str': force_authn_str,
                'is_passive_str': is_passive_str,
                'issue_instant': issue_instant,
                'destination': destination,
                'assertion_url': sp_data['assertionConsumerService']['url'],
                'entity_id': sp_data['entityId'],
                'nameid_policy_str': nameid_policy_str,
                'requested_authn_context_str': requested_authn_context_str,
                'attr_consuming_service_str': attr_consuming_service_str
        }
        self.__authn_request = request

    def get_request(self, deflate=True):
        """
        Returns unsigned AuthnRequest.
        :param deflate: It makes the deflate process optional
        :type: bool
        :return: AuthnRequest maybe deflated and base64 encoded
        :rtype: str object
        """
        if deflate:
            request = OneLogin_Saml2_Utils.deflate_and_base64_encode(
                self.__authn_request)
        else:
            request = b64encode(self.__authn_request)
        return request

    def get_id(self):
        """
        Returns the AuthNRequest ID.
        :return: AuthNRequest ID
        :rtype: string
        """
        return self.__id

    def get_xml(self):
        """
        Returns the XML that will be sent as part of the request
        :return: XML request body
        :rtype: string
        """
        return self.__authn_request


class SpidAuth(OneLogin_Saml2_Auth):

    def login(self, return_to=None, force_authn=False, is_passive=False, set_nameid_policy=True):
        """
        Initiates the SSO process.

        :param return_to: Optional argument. The target URL the user should be redirected to after login.
        :type return_to: string

        :param force_authn: Optional argument. When true the AuthNRequest will set the ForceAuthn='true'.
        :type force_authn: bool

        :param is_passive: Optional argument. When true the AuthNRequest will set the Ispassive='true'.
        :type is_passive: bool

        :param set_nameid_policy: Optional argument. When true the AuthNRequest will set a nameIdPolicy element.
        :type set_nameid_policy: bool

        :returns: Redirection URL
        :rtype: string
        """

        authn_request = SpidAuthnRequest(
            self._OneLogin_Saml2_Auth__settings, force_authn, is_passive, set_nameid_policy)
        self._OneLogin_Saml2_Auth__last_request = authn_request.get_xml()
        self._OneLogin_Saml2_Auth__last_request_id = authn_request.get_id()
        saml_request = authn_request.get_request()

        parameters = {'SAMLRequest': saml_request}
        if return_to is not None:
            parameters['RelayState'] = return_to
        else:
            parameters['RelayState'] = OneLogin_Saml2_Utils.get_self_url_no_query(
                self._OneLogin_Saml2_Auth__request_data)

        security = self._OneLogin_Saml2_Auth__settings.get_security_data()
        if security.get('authnRequestsSigned', False):
            parameters['SigAlg'] = security['signatureAlgorithm']
            parameters['Signature'] = self.build_request_signature(
                saml_request, parameters['RelayState'], security['signatureAlgorithm'])
        return self.redirect_to(self.get_sso_url(), parameters)


def init_saml_auth(req, config):
    current_ip = socket.gethostbyname(socket.gethostname())
    base_url = "https://{current_ip}".format(current_ip=current_ip)

    auth = SpidAuth(req, custom_base_path=pjoin('.', config['SAML_PATH']))
    sp_config = auth.get_settings().get_sp_data()
    sp_config["entityId"] = pjoin(base_url, "metadata")
    sp_config["assertionConsumerService"]["url"] = pjoin(base_url, "saml?acs")
    sp_config["singleLogoutService"]["url"] = pjoin(base_url, "saml?sls")

    organization = auth.get_settings().get_organization()
    organization["en-US"]["url"] = base_url

    idp_data = auth.get_settings().get_idp_data()
    if "idp_url" in config:
        try:
            idp_data.update(create_idp_config(config["idp_url"]))
            app.logger.warning("Updated config: {!r}".format(idp_data))
        except Exception as e:
            app.logger.warning(e)
    return auth


def create_idp_config(idp_metadata_url):
    def _get_item(item, key=None):
        tag = idp_metadata.findall(item)[0]
        if key:
            return dict(tag.items()).get(key)
        # Return the first text line.
        return next(tag.itertext())

    SSO = '//{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService'
    SLO = '//{urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService'
    X509 = '//{http://www.w3.org/2000/09/xmldsig#}X509Certificate'

    idp_metadata = download_idp_metadata(idp_metadata_url)
    return {
        "singleLogoutService": {
            "url": _get_item(SLO, 'Location'),
            "binding": _get_item(SLO, 'Binding')
        },
        "singleSignOnService": {
            "url": _get_item(SSO, 'Location'),
            "binding": _get_item(SSO, 'Binding')
        },
        "entityId": _get_item(".", "entityID"),
        "x509cert": encode_pem(_get_item(X509))
    }


def encode_pem(cert):
    if cert.startswith("-"):
        return cert

    return '\n'.join((
        "-----BEGIN CERTIFICATE-----",
        cert.strip("\n"),
        "-----END CERTIFICATE-----"
    ))


def download_idp_metadata(idp_metadata_url):
    idp_metadata = get(idp_metadata_url, verify=False, timeout=0.01)
    idp_metadata_xml = idp_metadata.content.decode()
    return parse(StringIO(idp_metadata_xml))


def test_init_saml_authapp():
    with app.test_request_context("/metadata"):
        req = prepare_flask_request(request)
        auth = init_saml_auth(req, app.config)
        current_ip = socket.gethostbyname(socket.gethostname())
        settings = auth.get_settings()
        assert current_ip in auth.get_settings().get_sp_data()["entityId"]


def prepare_flask_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'query_string': request.query_string
    }


def get_saml(sso=None, slo=None, return_to=""):
    req = prepare_flask_request(request)
    auth = init_saml_auth(req, app.config)
    errors = []
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    # Redirect requests to IdP
    if sso is not None:
        if not return_to:
            return redirect(auth.login())
        return_to = pjoin(request.host_url, return_to)
        return redirect(auth.login(return_to))

    if slo is not None:
        name_id = session.get('samlNameId')
        session_index = session.get('samlSessionIndex')
        return redirect(auth.logout(name_id=name_id, session_index=session_index))

    return problem(
        status=400,
        title="Bad Request",
        detail="Either `acs` or `sls` should be set.",
        ext=dict(
            errors=errors,
            not_auth_warn=not_auth_warn,
            success_slo=success_slo,
            attributes=attributes,
            ext={
                "_links": [
                    {"name": "Login URL", "url": pjoin(
                        request.url_root, "saml?sso")},
                    {"name": "Logout URL", "url": pjoin(
                        request.url_root, "saml?slo")}
                ]
            }
        )
    )


def post_saml(acs=None, sls=None):
    req = prepare_flask_request(request)
    auth = init_saml_auth(req, app.config)
    errors = []
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False
    app.logger.warning("acs: %r %r", acs, sls)
    # Inbound replies
    if acs is not None:
        auth.process_response()
        errors = auth.get_errors()

        if not auth.is_authenticated():
            return problem(status=401, title="Cannot Login", detail=errors)

        if not errors:
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            session['samlSessionIndex'] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if self_url != request.form.get('RelayState'):
                return redirect(auth.redirect_to(request.form['RelayState']))
            return problem(status=200, title="Login ok", detail="Login successful", ext={
                "_links": [
                    {"Current time": pjoin(request.url_root, "echo")},
                    {"Service status": pjoin(request.url_root, "status")}
                ]
            })
        return problem(status=401, title="Cannot Login", detail=errors)

    elif sls is not None:
        def dscb(): return session.clear()
        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)
            return problem(status=200, title="Logout ok", detail="Logout ok")
        return problem(status=500, title="Cannot Logout", ext=dict(errors=errors))

    return problem(
        status=400,
        title="Bad Request",
        detail="Either `acs` or `sls` should be set.",
        ext=dict(
            errors=errors,
            not_auth_warn=not_auth_warn,
            success_slo=success_slo,
            attributes=attributes,
            paint_logout=paint_logout
        )
    )


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
