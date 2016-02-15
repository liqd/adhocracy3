"""Euth subscribers."""
from substanced.util import find_service
from pyramid.settings import asbool

from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.resources.root import IRootPool
from adhocracy_core.sheets.principal import IGroup
from adhocracy_core.utils import get_sheet


def _remove_participant_from_authenticated_group(event):
    """Remove participant role from the authenticated group.

    Normally users who register are in the 'authenticated' group who
    has the 'participant' role. For Euth we remove the 'participant'
    role from this group, to allow private processes to be created.
    This is needed because 'participant' get a global 'view'
    permission and could use it to read a private process.
    """
    registry = event.registry
    if not asbool(registry.settings.get('adhocracy.add_default_group', True)):
        return
    root = event.object
    groups = find_service(root, 'principals', 'groups')
    authenticated = groups.get('authenticated')
    sheet = get_sheet(authenticated, IGroup)
    values = sheet.get()
    values['roles'].remove('participant')
    sheet.set(values)


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_remove_participant_from_authenticated_group,
                          IResourceCreatedAndAdded,
                          object_iface=IRootPool)
