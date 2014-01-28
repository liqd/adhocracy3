"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface

import colander


@provider(IISheet)
class IVersionable(ISheet):

    """Make this Fubel versionable."""

    taggedValue('schema', 'adhocracy.sheets.versions.VersionableSchema')


# class IForkable(IVersionable):
# """Marker interface representing a forkable node with version data"""

class VersionableSchema(colander.Schema):

    """Colander schema for IVersionable."""

    follows = ReferenceSetSchemaNode(default=[],
                                     missing=colander.drop,
                                     interfaces=[IVersionable]
                                     )
    """follows"""

# followed_by = ReferenceSetSchemaNode(
#         default=[],
#         missing=colander.drop,
#         interface=IVersionable,
#         readonly=True,
#     )


@provider(IISheet)
class IVersions(ISheet):

    """Dag for collecting all versions of one Fubel."""

    taggedValue('schema', 'adhocracy.sheets.versions.VersionsSchema')


class VersionsSchema(colander.Schema):

    """Colander schema for IVersions."""

    elements = ReferenceSetSchemaNode(default=[],
                                      missing=colander.drop,
                                      interface=[IVersionable],
                                      )


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
                                    (IVersionable, IInterface),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IVersions, IInterface),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (ITags, IInterface),
                                    IResourcePropertySheet)
