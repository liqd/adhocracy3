"""Root resource type."""
from pyramid.registry import Registry
from pyramid.security import Allow

from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.root import root_meta
from adhocracy_core.resources.root import create_initial_content_for_app_root
from adhocracy_core.schema import ACM
from adhocracy_core import sheets
from adhocracy_mercator.resources.mercator import IProcess
from pyramid.request import Request
from pyramid.security import ALL_PERMISSIONS


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
    request = Request.blank('/dummy')
    request.root = root
    request.registry = registry
    request.__cached_principals__ = ['role:god']
    mercator_process = root['mercator']
    workflow = registry.content.workflows['mercator']
    workflow.initialize(mercator_process)
    workflow.transition_to_state(mercator_process, request, 'announce')
    workflow.transition_to_state(mercator_process, request, 'participate')


mercator_acm = ACM().deserialize(
    {'principals':                                   ['anonymous', 'participant', 'moderator',  'creator', 'initiator', 'admin'],  # noqa
     'permissions': [['view_sheet_heardfrom',          None,        None,          None,          Allow,     Allow,       Allow],  # noqa
                     ]})


mercator_root_meta = root_meta._replace(
    after_creation=[create_initial_content_for_app_root,
                    add_mercator_process,
                    initialize_workflow
                    ])


def includeme(config):
    """Add resource type to content."""
    # overrides adhocracy root
    config.commit()
    add_resource_type_to_registry(mercator_root_meta, config)
