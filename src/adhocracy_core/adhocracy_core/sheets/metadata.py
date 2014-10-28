"""Metadata Sheet."""
from datetime import datetime

import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.events import ResourceSheetModified
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Reference
from adhocracy_core.utils import get_sheet


class IMetadata(ISheet):

    """Market interface for the metadata sheet."""


class MetadataCreatorsReference(SheetToSheet):

    """Metadata sheet creators reference."""

    source_isheet = IMetadata
    source_isheet_field = 'creator'
    target_isheet = IUserBasic


def resource_modified_metadata_subscriber(event):
    """Update the `modification_date` metadata."""
    sheet = get_sheet(event.object, IMetadata, registry=event.registry)
    sheet.set({'modification_date': datetime.now()},
              send_event=False,
              registry=event.registry,
              request=event.request,
              force=True)


class MetadataSchema(colander.MappingSchema):

    """Metadata sheet data structure.

    `creation_date`: Creation date of this resource. defaults to now.
    `item_creation_date`: Equals creation date for ISimple/IPool, equals
                          the item creation date for
                          :class:`adhocracy_core.interfaces.IItemVersion`.
                          This exists to ease the frontend end development.
                          This may go away if we have a high level API
                          to make :class:`adhocracy_core.interfaces.Item`
                         /`IItemVersion` one `thing`.
                         defaults to now.
    `modification_date`: Modification date of this resource. defaults to now.
    `creator`: creator (list of user resources) of this resource.
    `deleted`: whether the resource is marked as deleted (only shown to those
               that specifically ask for it)
    `hidden`: whether the resource is marked as hidden (only shown to those
               that have special permissions and ask for it)
    """

    creator = Reference(reftype=MetadataCreatorsReference, readonly=True)
    creation_date = DateTime(missing=colander.drop, readonly=True)
    item_creation_date = DateTime(missing=colander.drop, readonly=True)
    modification_date = DateTime(missing=colander.drop, readonly=True)
    deleted = Boolean()
    hidden = Boolean()


metadata_metadata = sheet_metadata_defaults._replace(
    isheet=IMetadata,
    schema_class=MetadataSchema,
    editable=True,
    creatable=True,
    readable=True,
)


def includeme(config):
    """Register sheets, add subscriber to update creation/modification date."""
    add_sheet_to_registry(metadata_metadata, config.registry)
    config.add_subscriber(resource_modified_metadata_subscriber,
                          ResourceSheetModified,
                          interface=IMetadata)
