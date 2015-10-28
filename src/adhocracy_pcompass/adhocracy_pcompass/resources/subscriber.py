"""Sync external ressources with elastic search."""

import re
import requests
import logging

from adhocracy_core.interfaces import ISheetBackReferenceAdded
from adhocracy_core.interfaces import ISheetBackReferenceModified
from adhocracy_core.resources.external_resource import IExternalResource
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.comment import ICommentable
from adhocracy_core.utils import get_sheet_field

log = logging.getLogger(__name__)


def notify_policy_compass(event):
    """Send notification to policy compass to reindex an external resource."""
    external_resource = event.object

    if external_resource is None:  # pragma: no cover
        return

    resource_name = get_sheet_field(external_resource, IName, 'name')
    match = re.match(
        '(?P<type>visualization|event|dataset|metric|fuzzymap|indicator)'
        '_(?P<id>[0-9]+)',
        resource_name)

    # this is not a known policycompass external resource
    if match is None:  # pragma: no cover
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
    config.add_subscriber(notify_policy_compass,
                          ISheetBackReferenceModified,
                          object_iface=IExternalResource,
                          event_isheet=ICommentable)
    config.add_subscriber(notify_policy_compass,
                          ISheetBackReferenceAdded,
                          object_iface=IExternalResource,
                          event_isheet=ICommentable)
