"""Root resource type."""
from pyramid.registry import Registry
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.root import create_initial_content_for_app_root
from adhocracy_core.resources.root import add_example_process
from adhocracy_core.resources.root import root_meta
from adhocracy_core.schema import ACM
from adhocracy_spd.resources.digital_leben import IProcess
import adhocracy_core.sheets


def add_spd_process(context: IPool, registry: Registry, options: dict):
    """Add spd specific process."""
    appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                  {'name': 'digital_leben'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context,
                            appstructs=appstructs)


spd_acm = ACM().deserialize(
    {'principals': ['anonymous', 'participant', 'moderator',  'creator', 'initiator', 'admin'],  # noqa
     'permissions': []})


spd_root_meta = root_meta._replace(
    after_creation=(create_initial_content_for_app_root,
                    add_spd_process,
                    add_example_process,
                    ))


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(spd_root_meta, config)
