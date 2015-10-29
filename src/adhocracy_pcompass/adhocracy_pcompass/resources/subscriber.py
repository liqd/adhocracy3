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
    settings = event.registry.settings
    endpoint = _get_index_endpoint(external_resource, settings)
    response = requests.post(endpoint)
    if response.status_code != 200:  # indexing error on pcompass
        msg = 'Notifying policy compass "{}" failed with "{}"'.format(
            endpoint, response.text)
        raise ValueError(msg)


def _get_index_endpoint(context: IExternalResource, settings: dict) -> str:
    resource_name = get_sheet_field(context, IName, 'name')
    match = re.match(
        '(?P<type>visualization|event|dataset|metric|fuzzymap|indicator)'
        '_(?P<id>[0-9]+)',
        resource_name)

    if match is None:  # pragma: no cover
        msg = 'This is not a known policy compass resource type'
        raise ValueError(msg)

    resource_type = match.group('type')
    resource_id = match.group('id')

    base_url = settings.get('adhocracy_pcompass.pcompass_endpoint',
                            'http://localhost:8000')
    endpoint = '{base}/api/v1/searchmanager/updateindexitem/{type}/{id_}'\
        .format(base=base_url,
                type=resource_type,
                id_=resource_id)
    return endpoint


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
