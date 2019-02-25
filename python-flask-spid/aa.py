import argparse
from base64 import decodestring
from logging import basicConfig
from logging.config import dictConfig
from os.path import dirname, isfile, join as pjoin
from attribute_authority.crypto import mkcert

from socket import gethostbyname, gethostname
import connexion
import yaml
from flask import current_app as app
from flask import request
from attribute_authority.crypto import init_certs


def configure_logger(log_config='logging.yaml'):
    """Configure the logging subsystem."""
    if not isfile(log_config):
        return basicConfig()

    with open(log_config) as fh:
        log_config = yaml.load(fh)
        return dictConfig(log_config)


def log_it():
    saml_response = request.form.get("SAMLResponse", "")
    app.logger.debug(decodestring(saml_response))



if __name__ == "__main__":
    # configure_logger()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--insecure-add-idp', dest='insecure_idp', required=False,
        help='Point to the IdP metadata URL', default=False,
    )
    parser.add_argument(
        '--insecure-add-aa', dest='insecure_aa', required=False,
        help='Point to the AA metadata URL', default=False
    )
    parser.add_argument(
        '--port', dest='port', required=False,
        help='Port', default=443
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=443, specification_dir='./', )
    # zapp.app.config['SECRET_KEY'] = 'onelogindemopytoolkit'
    # zapp.app.config['SAML_PATH'] = pjoin(dirname(__file__), 'saml')
    zapp.app.config.update(init_certs())

    if args.insecure_idp:
        zapp.app.config["idp_url"] = args.insecure_idp
    if args.insecure_aa:
        zapp.app.config["aa_url"] = args.insecure_aa

    zapp.app.before_request(log_it)
    zapp.add_api('attribute_authority/attribute-authority.yaml', arguments={'title': 'A simple Attribute Authority.'})
    zapp.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
