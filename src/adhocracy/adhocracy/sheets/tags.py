"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.versions import IVersionable
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface

import colander


@provider(IISheet)
class ITag(ISheet):

    """List all tags for this FubelVersionsPool."""

    taggedValue('schema', 'adhocracy.sheets.tags.TagSchema')


class TagSchema(colander.Schema):

    """Colander schema for ITags."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interface=IVersionable,
                                      )


@provider(IISheet)
class ITags(ISheet):

    """List all tags for this FubelVersionsPool."""

    taggedValue('schema', 'adhocracy.sheets.tags.TagsSchema')


class TagsSchema(colander.Schema):

    """Colander schema for ITags."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interface=ITag,
                                      )


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITag, IInterface),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITags, IInterface),
                                    IResourcePropertySheet)
