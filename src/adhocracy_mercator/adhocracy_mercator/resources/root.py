"""Root resource type."""

from pyramid.registry import Registry

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.root import root_meta
from adhocracy_core.resources.root import create_initial_content_for_app_root
from adhocracy_core import sheets
from adhocracy_mercator.resources.mercator import IProcess
import adhocracy_core.resources.root


def add_mercator_process(context: IPool, registry: Registry, options: dict):
    """Add mercator specific content."""
    appstructs = {sheets.name.IName.__identifier__: {'name': 'mercator'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context,
                            appstructs=appstructs)


mercator_root_meta = root_meta._replace(
    after_creation=(create_initial_content_for_app_root,
                    add_mercator_process,
                    adhocracy_core.resources.root.add_example_process
                    ))


def includeme(config):
    """Add resource type to content."""
    # overrides adhocracy root
    config.commit()
    add_resource_type_to_registry(mercator_root_meta, config)
