"""Name Sheet."""
import colander

from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets.name import name_meta
from adhocracy_core.sheets import AnnotationStorageSheet


class DummyNameSheet(AnnotationStorageSheet):

    """Dummy sheet class without persistent data store."""

    _data = {}


dummy_name_metadata = name_meta._replace(sheet_class=DummyNameSheet)


class IExtendedName(name_meta.isheet):

    """Marker interface for the extended name sheet."""


class ExtendedNameSchema(name_meta.schema_class):

    """Data structure for the extended name sheet."""

    description_x = colander.SchemaNode(colander.String(),
                                        default='',
                                        missing=colander.drop)


extended_name_metadata = name_meta._replace(
    isheet=IExtendedName,
    schema_class=ExtendedNameSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(dummy_name_metadata, config.registry)
    add_sheet_to_registry(extended_name_metadata, config.registry)
