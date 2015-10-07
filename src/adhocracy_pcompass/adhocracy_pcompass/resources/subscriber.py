"""Sync external ressources with elastic search."""

import re
import requests
import logging

from pyramid.traversal import find_interface

from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.resources.comment import IComment
from adhocracy_core.resources.external_resource import IExternalResource
from adhocracy_core.sheets.name import IName
from adhocracy_core.utils import get_sheet_field

log = logging.getLogger(__name__)


def notify_policycompass(event):
    """Push comments of IExternalResource ressources to elastic search."""
    comment = event.object
    external_resource = find_interface(comment, IExternalResource)

    if external_resource is None:
        return

    resource_name = get_sheet_field(external_resource, IName, 'name')
    match = re.match(
        '(?P<type>visualization|event|dataset|metric|model|indicator)'
        '_(?P<id>[0-9]+)',
        resource_name)

    # this is not a known policycompass external resource
    if match is None:
        return

    resource_type = match.group('type')
    resource_id = match.group('id')

    settings = event.registry.settings
    pcompass_endpoint = settings.get('adhocracy_pcompass.pcompass_endpoint',
                                     'http://localhost:8000')
    url = '{base}/api/v1/searchmanager/updateindexitem/{res_type}/{res_id}' \
        .format(base=pcompass_endpoint,
                res_type=resource_type,
                res_id=resource_id)

    r = requests.post(url)
    if r.status_code != 200:  # indexing error on pcompass
        msg = 'Notifying policy compass about "{}_{}" failed with "{}"'.format(
            resource_type, resource_type, r.text)
        raise ValueError(msg)


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(notify_policycompass,
                          IResourceCreatedAndAdded,
                          object_iface=IComment)
    config.add_subscriber(notify_policycompass,
                          IResourceSheetModified,
                          object_iface=IComment)
