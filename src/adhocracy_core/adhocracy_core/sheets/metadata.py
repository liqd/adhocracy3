"""Metadata Sheet."""
from datetime import datetime
from logging import getLogger

from pyramid.registry import Registry
from pyramid.traversal import resource_path
import colander

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.events import ResourceSheetModified
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Reference
from adhocracy_core.utils import blocked_with_reason
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_user
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import is_deleted
from adhocracy_core.utils import is_hidden


logger = getLogger(__name__)


class IMetadata(ISheet):

    """Market interface for the metadata sheet."""


class MetadataCreatorsReference(SheetToSheet):

    """Metadata sheet creators reference."""

    source_isheet = IMetadata
    source_isheet_field = 'creator'
    target_isheet = IUserBasic


class MetadataModifiedByReference(SheetToSheet):

    """Points to the last person who modified a resource."""

    source_isheet = IMetadata
    source_isheet_field = 'modified_by'
    target_isheet = IUserBasic


def resource_modified_metadata_subscriber(event):
    """Update the `modified_by` and `modification_date` metadata."""
    sheet = get_sheet(event.object, IMetadata, registry=event.registry)
    request = event.request
    modified_by = None if request is None else get_user(request)
    sheet.set({'modified_by': modified_by,
               'modification_date': datetime.now()},
              send_event=False,
              registry=event.registry,
              request=request,
              omit_readonly=False)


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
    `creator`: creator (user resource) of this resource.
    `modified_by`: the last person (user resources) who modified a resource,
                   initally the creator
    `modification_date`: Modification date of this resource. defaults to now.
    `deleted`: whether the resource is marked as deleted (only shown to those
               that specifically ask for it)
    `hidden`: whether the resource is marked as hidden (only shown to those
               that have special permissions and ask for it)
    """

    creator = Reference(reftype=MetadataCreatorsReference, readonly=True)
    creation_date = DateTime(missing=colander.drop, readonly=True)
    item_creation_date = DateTime(missing=colander.drop, readonly=True)
    modified_by = Reference(reftype=MetadataModifiedByReference, readonly=True)
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


def index_creator(resource, default):
    """Return creator userid value for the creator index."""
    creator = get_sheet_field(resource, IMetadata, 'creator')
    if creator == '':  # FIXME the default value should be None
        return creator
    userid = resource_path(creator)
    return userid


def view_blocked_by_metadata(resource: IResource,
                             registry: Registry) -> dict:
    """
    Return a dict with an explanation if viewing this resource is not allowed.

    This is the case if the `deleted` or `hidden` flag is set on the resource
    or one of its parents. If the resource provides metadata, the date of the
    last change and its author are added to the result.

    Otherwise, None is returned which means that the resource is viewable.
    """
    block_reason = blocked_with_reason(resource)
    if block_reason is None:
        return None
    result = {'reason': block_reason}
    if IMetadata.providedBy(resource):
        metadata = get_sheet(resource, IMetadata, registry=registry)
        appstruct = metadata.get()
        result['modification_date'] = appstruct['modification_date']
        result['modified_by'] = appstruct['modified_by']
    return result


def index_visibility(resource, default):
    """Return value for the private_visibility index.

    The return value will be one of [visible], [deleted], [hidden], or
    [deleted, hidden].
    """
    result = []
    if is_deleted(resource):
        result.append('deleted')
    if is_hidden(resource):
        result.append('hidden')
    if not result:
        # resources that are neither deleted nor hidden are visible
        result.append('visible')
    return result


def includeme(config):
    """Register sheets, add subscriber to update creation/modification date."""
    add_sheet_to_registry(metadata_metadata, config.registry)
    config.add_subscriber(resource_modified_metadata_subscriber,
                          ResourceSheetModified,
                          interface=IMetadata)
    config.add_indexview(index_visibility,
                         catalog_name='adhocracy',
                         index_name='private_visibility',
                         context=IMetadata,
                         )
    config.add_indexview(index_creator,
                         catalog_name='adhocracy',
                         index_name='creator',
                         context=IMetadata,
                         )
