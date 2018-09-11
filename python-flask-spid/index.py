import logging
from os.path import dirname
from os.path import join as pjoin

import connexion
from flask import request

logging.basicConfig(level=logging.DEBUG)
root = logging.getLogger()


def loggala():
    print("Ciao")
    print(request.args, request.path, request.method, request.form)
    from base64 import decodestring
    saml_response = request.form.get("SAMLResponse", "")
    print(decodestring(saml_response))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--insecure-add-idp', dest='insecure_idp', required=False,
        help='Point to the IdP URL', default=False
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=80, specification_dir='./', )
    zapp.app.config['SECRET_KEY'] = 'onelogindemopytoolkit'
    zapp.app.config['SAML_PATH'] = pjoin('/code', dirname(__file__), 'saml')

    if args.insecure_idp:
        zapp.app.config["idp_url"] = args.insecure_idp

    zapp.app.before_request(loggala)
    zapp.add_api('openapi.yaml', arguments={'title': 'Hello World Example'})
    zapp.run(host='0.0.0.0', port=80, debug=True)
