"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceSetSchemaNode
from zope.interface import provider
from zope.interface import taggedValue

import colander


@provider(IIResourcePropertySheet)
class IVersionable(ISheet):

    """Make this item versionable."""

    taggedValue('field:follows',
                ReferenceSetSchemaNode(
                    default=[],
                    missing=colander.drop,
                    interfaces=['adhocracy.sheets.versions.IVersionable'],
                ))

# followed_by = ReferenceSetSchemaNode(
#         default=[],
#         missing=colander.drop,
#         interface=IVersionable,
#         readonly=True,
#     )
# FIXME: check constrains (ist the follwed node the right node?)


@provider(IIPool)
class IVersions(ISheet):

    """Dag for collecting all versions of one item."""

    taggedValue('field:elements',
                ReferenceSetSchemaNode(default=[],
                                       missing=colander.drop,
                                       interfaces=[IVersionable],
                                       )
                )


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IVersionable, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IVersions, IIPool),
                                    IResourcePropertySheet)
