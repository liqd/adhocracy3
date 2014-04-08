"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.versions import IVersionable
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceListSchemaNode
from zope.interface import provider
from zope.interface import taggedValue


@provider(IIResourcePropertySheet)
class ITag(ISheet):

    """List all tags for this Item."""

    taggedValue('field:elements',
                ReferenceListSchemaNode(
                    reftype='adhocracy.sheets.tags.ITagElementsReference',
                ))


class ITagElementsReference(AdhocracyReferenceType):

    """ITag reference."""

    source_isheet = ITag
    source_isheet_field = 'elements'
    target_isheet = IVersionable


@provider(IIPool)
class ITags(ISheet):

    """List all tags for this Item."""

    taggedValue('field:elements',
                ReferenceListSchemaNode(
                    reftype='adhocracy.sheets.tags.ITagsElementsReference',
                ))


class ITagsElementsReference(AdhocracyReferenceType):

    """ITags reference."""

    source_isheet = ITags
    source_isheet_field = 'elements'
    target_isheet = ITag


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITag, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (ITags, IIPool),
                                    IResourcePropertySheet)
