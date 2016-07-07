"""Notification Sheet."""
from pyramid.traversal import resource_path
from substanced.util import find_service

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import search_query
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import UniqueReferences


class INotification(ISheet):
    """Marker interface for the notification sheet."""


class IFollowable(ISheet):
    """Marker interface for resources that can be followed upon."""


class NotificationFollowReference(SheetToSheet):
    """Notification sheet follow reference."""

    source_isheet = INotification
    source_isheet_field = 'follow_resources'
    target_isheet = IFollowable


def get_follow_choices(context, request) -> []:
    """Return follow resources choices."""
    catalogs = find_service(context, 'catalogs')
    query = search_query._replace(interfaces=IFollowable)
    resources = catalogs.search(query).elements
    choices = [(request.resource_url(r), resource_path(r)) for r in resources]
    return choices


class NotificationSchema(MappingSchema):
    """Notification sheet data structure.

    `follow_resources`: Follow activities these resources are involved in.
    """

    follow_resources = UniqueReferences(reftype=NotificationFollowReference,
                                        choices_getter=get_follow_choices)


notification_meta = sheet_meta._replace(isheet=INotification,
                                        schema_class=NotificationSchema,
                                        permission_edit='edit_notification',
                                        )


followable_meta = sheet_meta._replace(isheet=IFollowable,
                                      editable=False,
                                      creatable=False,
                                      )


def includeme(config):
    """Register sheet."""
    add_sheet_to_registry(notification_meta, config.registry)
    add_sheet_to_registry(followable_meta, config.registry)
