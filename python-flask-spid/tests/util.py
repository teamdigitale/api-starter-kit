from connexion.resolver import Resolver


def noop(*args, **kwds):
    raise NotImplementedError


class FakeResolver(Resolver):
    def __init__(self, me):
        FakeResolver.__init__(self)
        self.me = me

    def resolve_operation_id(self, operation):
        """
        Mock operation id, just to validate API.
        :type operation: connexion.operations.AbstractOperation
        """
        oid = operation.operation_id
        if "." in oid:
            oid = oid.split(".")[-1]
        # Append the operation function to this module.
        setattr(self.me, oid, noop)
        return "test_oas." + oid
