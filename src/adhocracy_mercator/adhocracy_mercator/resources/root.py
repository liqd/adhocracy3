"""Root resource type."""
from pyramid.registry import Registry
from pyramid.security import Allow

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.resources.process import IProcess
from adhocracy_core.resources.root import root_meta
from adhocracy_core.resources.root import add_platform
from adhocracy_core.schema import ACM
from adhocracy_core import sheets


def _create_initial_content(context: IPool, registry: Registry, options: dict):
    """Add mercator specific content."""
    add_platform(context, registry, 'mercator', resource_type=IOrganisation)
    appstructs = {sheets.name.IName.__identifier__: {'name': 'advocate'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context['mercator'],
                            appstructs=appstructs)


mercator_acm = ACM().deserialize(
    {'principals':                                   ['anonymous', 'participant', 'moderator',  'creator', 'initiator', 'admin'],  # noqa
     'permissions': [['view_sheet_heardfrom',          None,        None,          None,          Allow,     Allow,       Allow],  # noqa
                     ]})


mercator_root_meta = root_meta._replace(after_creation=root_meta.after_creation
                                        + [_create_initial_content])


def includeme(config):
    """Add resource type to content."""
    # overrides adhocracy root
    config.commit()
    add_resource_type_to_registry(mercator_root_meta, config)