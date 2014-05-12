"""Sheets to work with versionable resources."""
from substanced.util import get_oid
from zope.interface import implementer
from zope.interface import provider
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface
import colander

from adhocracy.graph import get_back_references_for_isheet
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceListSchemaNode
from adhocracy.schema import ReferenceSetSchemaNode


class IIVersionable(IInterface):

    """Marker interfaces to register the versionable propertysheet adapter."""


@provider(IIVersionable)
class IVersionable(ISheet):

    """Make this item versionable."""

    taggedValue(
        'field:follows',
        ReferenceSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionableFollowsReference'
        ))
    taggedValue(
        'field:followed_by',
        ReferenceSetSchemaNode(
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
        ReferenceListSchemaNode(
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

    def _followed_by(self, resource):
        """Determine the successors ("followed_by") of a versionable resource.

        Args:
            resource (IResource that provides the IVersionable sheet)

        Returns:
            a list of OIDs of successor versions (possibly empty)

        """
        versions = get_back_references_for_isheet(resource, IVersionable)
        result = []
        for new_version in versions.get('follows', []):
            result.append(get_oid(new_version))
        return set(result)

    def get(self):
        """Return data struct."""
        struct = super().get()
        struct['followed_by'] = self._followed_by(self.context)
        return struct


def includeme(config):
    """Register adapters."""
    config.registry.registerAdapter(VersionableSheetAdapter,
                                    (IVersionable, IIVersionable),
                                    IResourcePropertySheet)
    config.registry.registerAdapter(PoolPropertySheetAdapter,
                                    (IVersions, IIPool),
                                    IResourcePropertySheet)
