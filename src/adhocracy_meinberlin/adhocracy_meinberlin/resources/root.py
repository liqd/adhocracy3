"""Root resource type."""
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.root import add_platform
from adhocracy_core.resources.root import root_meta
from .kiezkassen import IProcess
import adhocracy_core.sheets


def create_initial_content_for_meinberlin(context: IPool, registry: Registry,
                                          options: dict):
    """Add meinberlin specific example content."""
    registry = get_current_registry(context)
    add_platform(context, registry, 'organisation',
                 resource_type=IOrganisation)
    appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                  {'name': 'kiezkasse'},
                  adhocracy_core.sheets.title.ITitle.__identifier__:
                  {'title': 'Sample Kiezkassen process'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context['organisation'],
                            appstructs=appstructs)


meinberlin_root_meta = root_meta._replace(
    after_creation=root_meta.after_creation +
    [create_initial_content_for_meinberlin])


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(meinberlin_root_meta, config)
