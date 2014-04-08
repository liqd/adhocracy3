"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceSetSchemaNode
from adhocracy.schema import ReferenceListSchemaNode
from zope.interface import provider
from zope.interface import taggedValue

import colander


@provider(IIResourcePropertySheet)
class IVersionable(ISheet):

    """Make this item versionable."""

    taggedValue(
        'field:follows',
        ReferenceSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionableFollowsReference'
        ))


class IVersionableFollowsReference(AdhocracyReferenceType):

    """IVersionable reference."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


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

    taggedValue(
        'field:elements',
        ReferenceListSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionsElementsReference',
        ))


class IVersionsElementsReference(AdhocracyReferenceType):

    """IVersions reference."""

    source_isheet = IVersions
    source_isheet_field = 'elements'
    target_isheet = IVersionable


def includeme(config):
    """Register adapter."""
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (IVersionable, IIResourcePropertySheet),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IVersions, IIPool),
                                    IResourcePropertySheet)
