"""Sheets to work with versionable resources."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets.pool import PoolSheet
from adhocracy.schema import ListOfUniqueReferences


class IVersionable(ISheet):

    """Maker interface for resources with the versionable sheet."""


class VersionableFollowsReference(NewVersionToOldVersion):

    """versionable sheet reference to preceding versions."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


class VersionableSchema(colander.MappingSchema):

    """ Versionable sheet data structure.

    Set/get predecessor (`follows`) and get successor (`followed_by`) versions
    of this resource.
    """

    follows = ListOfUniqueReferences(reftype=VersionableFollowsReference)
    followed_by = ListOfUniqueReferences(readonly=True,
                                         backref=True,
                                         reftype=VersionableFollowsReference)


versionable_metadata = sheet_metadata_defaults._replace(
    isheet=IVersionable,
    schema_class=VersionableSchema,

)


class IVersions(ISheet):

    """Marker interface for the versions sheet."""


class IVersionsElementsReference(SheetToSheet):

    """version sheet elements reference."""

    source_isheet = IVersions
    source_isheet_field = 'elements'
    target_isheet = IVersionable


class VersionsSchema(colander.MappingSchema):

    """Versions sheet data structure.

    `elements`: Dag for collecting all versions of one item.
    """

    elements = ListOfUniqueReferences(
        reftype=IVersionsElementsReference)


versions_metadata = sheet_metadata_defaults._replace(
    isheet=IVersions,
    sheet_class=PoolSheet,
    schema_class=VersionsSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(versionable_metadata, config.registry)
    add_sheet_to_registry(versions_metadata, config.registry)
