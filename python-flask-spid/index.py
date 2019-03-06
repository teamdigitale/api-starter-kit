import argparse
from base64 import decodestring
from logging import basicConfig
from logging.config import dictConfig
from os.path import dirname, isfile
from os.path import join as pjoin
from socket import gethostbyname, gethostname

import connexion
from flask import current_app as app
from flask import request

import yaml


def configure_logger(log_config="logging.yaml"):
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
    configure_logger()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--insecure-add-idp",
        dest="insecure_idp",
        required=False,
        help="Point to the IdP metadata URL",
        default=False,
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=443, specification_dir="./")
    zapp.app.config["SECRET_KEY"] = "onelogindemopytoolkit"
    zapp.app.config["SAML_PATH"] = pjoin(dirname(__file__), "saml")

    current_ip = gethostbyname(gethostname())
    base_url = "https://{current_ip}".format(current_ip=current_ip)
    zapp.app.config["entityId"] = pjoin(base_url, "metadata")

    custom_base_path = pjoin(zapp.app.config["SAML_PATH"], "settings.json")
    with open(custom_base_path) as fh:
        saml_config = yaml.load(fh.read())
    zapp.app.config["x509cert"] = saml_config["sp"]["x509cert"]
    zapp.app.config["privateKey"] = saml_config["sp"]["privateKey"]

    if args.insecure_idp:
        zapp.app.config["idp_url"] = args.insecure_idp

    zapp.app.before_request(log_it)
    zapp.add_api("spid.yaml", arguments={"title": "Hello World Example"})
    zapp.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
