"""Root resource type."""
from pyramid.registry import Registry
from pyramid.security import Allow

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.root import root_meta
from adhocracy_core.resources.root import create_initial_content_for_app_root
from adhocracy_core.schema import ACM
from adhocracy_core.workflows import setup_workflow
from adhocracy_core import sheets
from adhocracy_mercator.resources.mercator import IProcess
from pyramid.security import ALL_PERMISSIONS
import adhocracy_core.resources.root


def add_mercator_process(context: IPool, registry: Registry, options: dict):
    """Add mercator specific content."""
    appstructs = {sheets.name.IName.__identifier__: {'name': 'mercator'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context,
                            appstructs=appstructs)


def initialize_workflow(context: IPool, registry: Registry, options: dict):
    """Initialize mercator workflow."""
    root = context
    # at this point the permissions are not setup so we need to add
    # the god's permissions
    root.__acl__ = [(Allow, 'role:god', ALL_PERMISSIONS)]
    mercator_process = root['mercator']
    setup_workflow(mercator_process, ['announce', 'participate'], registry)


mercator_acm = ACM().deserialize(
    {'principals':                                   ['anonymous', 'participant', 'moderator',  'creator', 'initiator', 'admin'],  # noqa
     'permissions': [['view_sheet_heardfrom',          None,        None,          None,         Allow,     Allow,       Allow],  # noqa
                     ['edit_mercator_proposal',        None,        None,          None,         None,      None,        Allow],  # noqa
                     ['create_mercator_proposal',      None,        None,          None,         None,      None,        Allow],  # noqa
                     ]})


mercator_root_meta = root_meta._replace(
    after_creation=[create_initial_content_for_app_root,
                    add_mercator_process,
                    initialize_workflow,
                    adhocracy_core.resources.root.add_example_process
                    ])


def includeme(config):
    """Add resource type to content."""
    # overrides adhocracy root
    config.commit()
    add_resource_type_to_registry(mercator_root_meta, config)
