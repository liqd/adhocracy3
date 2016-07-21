"""Metadata Sheet."""
from logging import getLogger

from colander import deferred
from colander import drop
from pyramid.registry import Registry

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import AttributeResourceSheet
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.schema import create_deferred_permission_validator
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Reference
from adhocracy_core.utils import now


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


@deferred
def deferred_check_hide_permission(node, kw) -> deferred:
    """Check hide_permission."""
    validator = create_deferred_permission_validator('hide')
    return validator(node, kw)


class MetadataSchema(MappingSchema):
    """Metadata sheet data structure.

    `creation_date`: Creation date of this resource. defaults to now.

    `item_creation_date`: Equals creation date for ISimple/IPool,
    equals the item creation date for
    :class:`adhocracy_core.interfaces.IItemVersion`. This exists to
    ease the frontend end development. This may go away if we have a
    high level API to make :class:`adhocracy_core.interfaces.Item` /
    `IItemVersion` one `thing`. Defaults to now.

    `creator`: creator (user resource) of this resource.

    `modified_by`: the last person (user resources) who modified a
    resource, initially the creator

    `modification_date`: Modification date of this resource. defaults to now.

    `hidden`: whether the resource is marked as hidden (only shown to those
    that have special permissions and ask for it)

    """

    creator = Reference(reftype=MetadataCreatorsReference, readonly=True)
    creation_date = DateTime(missing=drop, readonly=True)
    item_creation_date = DateTime(missing=drop, readonly=True)
    modified_by = Reference(reftype=MetadataModifiedByReference, readonly=True)
    modification_date = DateTime(missing=drop, readonly=True)
    hidden = Boolean(validator=deferred_check_hide_permission)


metadata_meta = sheet_meta._replace(
    isheet=IMetadata,
    schema_class=MetadataSchema,
    sheet_class=AttributeResourceSheet,
    editable=True,
    creatable=True,
    readable=True,
    permission_edit='delete',
)


def view_blocked_by_metadata(resource: IResource, registry: Registry,
                             block_reason: str) -> dict:
    """
    Return a dict with an explanation why viewing this resource is not allowed.

    If the resource provides metadata, the date of the
    last change and its author are added to the result.
    """
    result = {'reason': block_reason}
    if not IMetadata.providedBy(resource):
        return result
    metadata = registry.content.get_sheet(resource, IMetadata)
    appstruct = metadata.get()
    result['modification_date'] = appstruct['modification_date']
    result['modified_by'] = appstruct['modified_by']
    return result


def is_older_than(resource: IMetadata, days: int) -> bool:
    """Check if the creation date of `context` is older than `days`."""
    timedelta = now() - resource.creation_date
    return timedelta.days > days


def includeme(config):
    """Register sheets, add subscriber to update creation/modification date."""
    add_sheet_to_registry(metadata_meta, config.registry)
