"""Sheets to work with versionable resources."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IIResourcePropertySheet
from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.sheets import ResourcePropertySheetAdapter
from adhocracy.sheets.pool import PoolPropertySheetAdapter
from adhocracy.sheets.pool import IIPool
from adhocracy.schema import ReferenceListSchemaNode
from adhocracy.schema import ReferenceSetSchemaNode
from pyramid.traversal import resource_path
from substanced.util import find_objectmap
from zope.interface import provider
from zope.interface import taggedValue

import colander


def followed_by(resource):
    """Determine the successors ("followed_by") of a versionable resource.

    Args:
        resource (IResource that implements the IVersionable sheet)

    Returns:
        a list of resource paths to successor versions (possibly empty)

    """
    om = find_objectmap(resource)
    result = []
    if om is not None:
        for source in om.sources(resource, IVersionableFollowsReference):
            result.append(resource_path(source))
    return result


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
    taggedValue(
        'field:followed_by',
        ReferenceSetSchemaNode(
            default=[],
            missing=colander.drop,
            reftype='adhocracy.sheets.versions.IVersionableFollowedByReference'
        ))


class IVersionableFollowsReference(AdhocracyReferenceType):

    """IVersionable reference to preceding versions."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


class IVersionableFollowedByReference(AdhocracyReferenceType):

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
