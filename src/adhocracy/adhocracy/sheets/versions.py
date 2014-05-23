"""Sheets to work with versionable resources."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.sheets import GenericResourceSheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets.pool import PoolSheet
from adhocracy.schema import ListOfUniqueReferences


class IVersionable(ISheet):

    """Maker interface for resources with the versionable sheeet."""


class IVersionableFollowsReference(NewVersionToOldVersion):

    """versionable sheet reference to preceding versions."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


class IVersionableFollowedByReference(SheetToSheet):

    """BackReference for the IVersionableFollowsReference, not stored."""

    source_isheet = IVersionable
    source_isheet_field = 'followed_by'
    target_isheet = IVersionable


class VersionableSchema(colander.MappingSchema):

    """ Versionable sheet data structure.

    Set/get precssor (`follows`) and get successor (`followed_by`) versions
    of this resource.

    """

    follows = ListOfUniqueReferences(reftype=IVersionableFollowsReference)
    followed_by = ListOfUniqueReferences(
        reftype=IVersionableFollowedByReference)


class VersionableSheet(GenericResourceSheet):

    """Sheet to set/get the versionable data structure."""

    isheet = IVersionable
    schema_class = VersionableSchema

    def set(self, appstruct, omit=()):
        if 'followed_by' in appstruct:
            del appstruct['followed_by']
        super().set(appstruct, omit)

    def get(self):
        """Return appstruct."""
        #FIXME: import is temporally workaround to make unit test mocking work
        from adhocracy.graph import get_followed_by
        from adhocracy.graph import get_follows
        struct = super().get()
        struct['followed_by'] = get_followed_by(self.context)
        struct['follows'] = get_follows(self.context)
        return struct


versionable_metadata = sheet_metadata_defaults._replace(
    isheet=IVersionable,
    sheet_class=VersionableSheet,
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
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(versionable_metadata, config.registry)
    add_sheet_to_registry(versions_metadata, config.registry)
