"""Sync external ressources with elastic search."""

import re
import requests
import logging

from substanced.util import find_service
from pyramid.traversal import find_interface

from adhocracy_core.interfaces import IResourceCreatedAndAdded, search_query
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.resources.comment import IComment
from adhocracy_core.resources.external_resource import IExternalResource
from adhocracy_core.sheets.name import IName
from adhocracy_core.utils import get_sheet_field

log = logging.getLogger(__name__)


def update_elasticsearch_policycompass(event):
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

    # count comments using catalog
    catalogs = find_service(external_resource, 'catalogs')
    query = search_query._replace(interfaces=IComment, only_visible=True)
    comment_count = catalogs.search(query).count

    settings = event.registry.settings
    es_endpoint = settings.get('adhocracy_pcompass.elasticsearch_endpoint',
                               'http://localhost:9000')
    es_index = settings.get('adhocracy_pcompass.elasticsearch_index',
                            'policycompass_search')
    r = requests.post('{url}/{index}/{res_type}/{res_id}/_update'.format(
        url=es_endpoint,
        index=es_index,
        res_type=resource_type,
        res_id=resource_id),
        json={'doc': {'comment_count': comment_count}})

    if r.status_code == 404:  # document not created (error in pcompass)
        log.warn('Document "{}/{}" is missing from elastic search "{}" index'
                 .format(resource_type, resource_id, es_index))
    elif r.status_code >= 400:  # unexpected error occured
        msg = 'Update elastic search index "{}" failed with "{}"'.format(
            es_index, r.text)
        raise ValueError(msg)


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(update_elasticsearch_policycompass,
                          IResourceCreatedAndAdded,
                          object_iface=IComment)
    config.add_subscriber(update_elasticsearch_policycompass,
                          IResourceSheetModified,
                          object_iface=IComment)
