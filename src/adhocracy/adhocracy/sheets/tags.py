"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.versions import IVersionable
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue

import colander


@provider(IIResourcePropertySheet)
class ITag(ISheet):

    """List all tags for this FubelVersionsPool."""

    taggedValue('schema', 'adhocracy.sheets.tags.TagSchema')


class TagSchema(colander.Schema):

    """Colander schema for ITags."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interface=IVersionable,
                                      )


@provider(IIPool)
class ITags(ISheet):

    """List all tags for this FubelVersionsPool."""

    taggedValue('schema', 'adhocracy.sheets.tags.TagsSchema')


class TagsSchema(colander.Schema):

    """Colander schema for ITags."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interfaces=[ITag],
                                      )


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITag, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (ITags, IIPool),
                                    IResourcePropertySheet)
