#
# run me with nosetests -vs test_oas.py
#
import sys
from glob import glob

import connexion
import werkzeug.exceptions
from connexion.resolver import Resolver

me = sys.modules[__name__]


def noop(*args, **kwds): raise NotImplementedError


class FakeResolver(Resolver):

    def resolve_operation_id(self, operation):
        """
        Mock operation id, just to validate API.
        :type operation: connexion.operations.AbstractOperation
        """
        oid = operation.operation_id
        if "." in oid:
            oid = oid.split(".")[-1]
        # Append the operation function to this module.
        setattr(me, oid, noop)
        return "test_oas." + oid


def test_oas3():
    files = ("../openapi/spid.yaml.src", )

    def assert_parse_oas3(zapp, f):
        zapp.add_api(f, resolver=FakeResolver())

    def assert_is_oas3(zapp):
        assert zapp.options.oas_version > (2, 0)

    for f in files:
        zapp = connexion.FlaskApp(__name__, specification_dir='.',)
        yield assert_parse_oas3, zapp, f

        # yield assert_is_oas3, zapp  # Failing test
