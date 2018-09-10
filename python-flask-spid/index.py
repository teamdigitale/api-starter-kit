import logging
import socket
from base64 import b64encode
from os.path import dirname
from os.path import join as pjoin
from urlparse import urlparse

from flask import (Flask, make_response, redirect, render_template, request,
                   session)
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

logging.basicConfig(level=logging.DEBUG)
root = logging.getLogger()

import connexion



app = Flask(__name__)
app.config['SECRET_KEY'] = 'onelogindemopytoolkit'
app.config['SAML_PATH'] = pjoin('/code', dirname(__file__), 'saml')


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


def init_saml_auth(req):
    current_ip = socket.gethostbyname(socket.gethostname())
    base_url = "http://{current_ip}".format(current_ip=current_ip)

    auth = SpidAuth(req, custom_base_path=pjoin('.', app.config['SAML_PATH']))
    sp_config = auth.get_settings().get_sp_data()
    sp_config["entityId"] = pjoin(base_url, "metadata/")
    sp_config["assertionConsumerService"]["url"] = pjoin(base_url, "?acs")
    sp_config["singleLogoutService"]["url"] = pjoin(base_url, "?sls")

    organization = auth.get_settings().get_organization()
    organization["en-US"]["url"] = base_url

    idp_config = auth.get_settings().get_idp_data()
    if "idp_url" in app.config:
        idp_config["singleLogoutService"]["url"] = pjoin(
            app.config["idp_url"], 'slo')
        idp_config["singleSignOnService"]["url"] = pjoin(
            app.config["idp_url"], 'sso')
        idp_config["entityId"] = app.config["idp_url"]

    return auth


def test_init_saml_auth():
    with app.test_request_context("/metadata"):
        req = prepare_flask_request(request)
        auth = init_saml_auth(req)
        current_ip = socket.gethostbyname(socket.gethostname())
        settings = auth.get_settings()
        assert current_ip in auth.get_settings().get_sp_data()["entityId"]
        raise NotImplementedError


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


@app.route('/', methods=['GET', 'POST'])
def index():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    errors = []
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    if 'sso' in request.args:
        return redirect(auth.login())

    if 'sso2' in request.args:
        return_to = '%sattrs/' % request.host_url
        return redirect(auth.login(return_to))

    if 'slo' in request.args:
        name_id = session.get('samlNameId')
        session_index = session.get('samlSessionIndex')
        return redirect(auth.logout(name_id=name_id, session_index=session_index))

    if 'acs' in request.args:
        auth.process_response()
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            session['samlSessionIndex'] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if self_url != request.form.get('RelayState'):
                return redirect(auth.redirect_to(request.form['RelayState']))

    elif 'sls' in request.args:
        def dscb(): return session.clear()
        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)
            else:
                success_slo = True

    if 'samlUserdata' in session:
        paint_logout = True
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    return render_template(
        'index.html',
        errors=errors,
        not_auth_warn=not_auth_warn,
        success_slo=success_slo,
        attributes=attributes,
        paint_logout=paint_logout
    )


@app.before_request
def loggala():
    print("Ciao")
    print(request.args, request.path, request.method, request.form)
    from base64 import decodestring
    saml_response = request.form.get("SAMLResponse", "")
    print(decodestring(saml_response))


@app.route('/attrs/')
def attrs():
    paint_logout = False
    attributes = False

    if 'samlUserdata' in session:
        paint_logout = True
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    return render_template('attrs.html', paint_logout=paint_logout,
                           attributes=attributes)


@app.route('/metadata/')
def metadata():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--insecure-add-idp', dest='insecure_idp', required=False,
        help='Point to the IdP URL', default=False
    )
    args = parser.parse_args()
    if args.insecure_idp:
        app.config["idp_url"] = args.insecure_idp
    app.run(host='0.0.0.0', port=80, debug=True)
