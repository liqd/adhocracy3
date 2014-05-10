"""Sheets to work with versionable resources."""
from adhocracy.graph import get_followed_by
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceListSetSchemaNode
from zope.interface import implementer
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface

import colander


class IIVersionable(IInterface):

    """Marker interfaces to register the versionable propertysheet adapter."""


@provider(IIVersionable)
class IVersionable(ISheet):

    """Make this item versionable."""

    taggedValue(
        'field:follows',
        ReferenceListSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionableFollowsReference'
        ))
    taggedValue(
        'field:followed_by',
        ReferenceListSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionableFollowedByReference'
        ))


class IVersionableFollowsReference(NewVersionToOldVersion):

    """IVersionable reference to preceding versions."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


class IVersionableFollowedByReference(SheetToSheet):

    """IVersionable reference to subsequent versions.

    Not stored in DB, but auto-calculated on demand.

    """

    source_isheet = IVersionable
    source_isheet_field = 'followed_by'
    target_isheet = IVersionable


@provider(IIPool)
class IVersions(ISheet):

    """Dag for collecting all versions of one item."""

    taggedValue(
        'field:elements',
        ReferenceListSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionsElementsReference',
        ))


class IVersionsElementsReference(SheetToSheet):

    """IVersions reference."""

    source_isheet = IVersions
    source_isheet_field = 'elements'
    target_isheet = IVersionable


@implementer(IResourcePropertySheet)
class VersionableSheetAdapter(ResourcePropertySheetAdapter):

    """Adapts versionable resources to substanced PropertySheet."""

    def get(self):
        """Return data struct."""
        struct = super().get()
        followed_by = get_followed_by(self.context)
        struct['followed_by'] = list(followed_by)
        return struct


def includeme(config):
    """Register adapters."""
    config.registry.registerAdapter(VersionableSheetAdapter,
                                    (IVersionable, IIVersionable),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IVersions, IIPool),
                                    IResourcePropertySheet)
