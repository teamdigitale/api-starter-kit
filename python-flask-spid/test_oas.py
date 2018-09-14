import connexion
from connexion import problem
from connexion.resolver import Resolver


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


def test_oas3():
    for f in (
            'spid.yaml.src',
    ):
        zapp = connexion.FlaskApp(__name__, specification_dir='.',)
        yield zapp.add_api, f


def test_problem():
    problem(status=401,
            title="Unauthorized",
            detail="foo",
            ext={
                "_links": [
                    {"href": "bar"}
                ]
            })
