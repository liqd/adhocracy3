"""Sheets to work with versionable resources."""
from adhocracy.interfaces import (
    ISheet,
    IISheet,
    IResourcePropertySheet,
)
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.versions import IVersionable
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import (
    provider,
    taggedValue,
)
from zope.interface.interfaces import IInterface

import colander


@provider(IISheet)
class ITags(ISheet):

    """List all tags for this FubelVersionsPool."""

    taggedValue('schema', 'adhocracy.sheets.tags.TagsSchema')


class TagsSchema(colander.Schema):

    """Colander schema for ITags."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interface=IVersionable,
                                      )


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITags, IInterface),
                                    IResourcePropertySheet)
