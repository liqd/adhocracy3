"""Euth subscribers."""
from substanced.util import find_service
from pyramid.settings import asbool
from pyramid.events import ApplicationCreated

from adhocracy_core.authorization import set_acms_for_app_root
from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.resources.root import IRootPool
from adhocracy_core.resources.root import root_acm
from adhocracy_core.sheets.principal import IGroup
from adhocracy_core.utils import get_sheet
from adhocracy_euth.resources.root import euth_acm


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


def set_root_acms(event):
    """Set :term:`acm`s for root if the Pyramid application starts."""
    set_acms_for_app_root(event.app, (euth_acm, root_acm))


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(_remove_participant_from_authenticated_group,
                          IResourceCreatedAndAdded,
                          object_iface=IRootPool)
    config.add_subscriber(set_root_acms, ApplicationCreated)
