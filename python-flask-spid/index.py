import argparse
import logging
from base64 import decodestring
from os.path import dirname
from os.path import join as pjoin

import connexion
from connexion.resolver import Resolver
from flask import request

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def log_it():
    saml_response = request.form.get("SAMLResponse", "")
    log.debug(decodestring(saml_response))


class PonyResolver(Resolver):

    def __init__(self, namespace):
        Resolver.__init__(self)
        self.namespace = namespace

    def resolve_operation_id(self, operation):
        """
        Default operationId resolver

        :type operation: connexion.operations.AbstractOperation
        """
        operation_id = operation.operation_id
        router_controller = operation.router_controller or self.namespace
        if router_controller is None:
            return operation_id
        return '{}.{}'.format(router_controller, operation_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--insecure-add-idp', dest='insecure_idp', required=False,
        help='Point to the IdP metadata URL', default=False
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=443, specification_dir='./', )
    zapp.app.config['SECRET_KEY'] = 'onelogindemopytoolkit'
    zapp.app.config['SAML_PATH'] = pjoin(dirname(__file__), 'saml')

    if args.insecure_idp:
        zapp.app.config["idp_url"] = args.insecure_idp

    zapp.app.before_request(log_it)
    zapp.add_api('spid.yaml', arguments={'title': 'Hello World Example'})
    zapp.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
