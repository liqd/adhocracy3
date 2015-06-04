"""Basic organisation pool to structure processes."""
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.process import IProcess


class IOrganisation(IPool):

    """Organisation Pool."""


organisation_meta = pool_meta._replace(
    iresource=IOrganisation,
    permission_create='create_organisation',
    is_implicit_addable=True,
    element_types=[IProcess,
                   IOrganisation,
                   ],
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(organisation_meta, config)
