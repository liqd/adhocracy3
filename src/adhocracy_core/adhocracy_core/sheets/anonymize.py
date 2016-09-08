"""Sheet to allow adding children annonymized."""
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import MappingSchema


ANONYMIZE_PERMISSION = 'manage_anonymized'


class IAllowAddAnonymized(ISheet):
    """Marker interface for the allow_add_anonymized sheet."""


class AllowAddAnonymizedSchema(MappingSchema):
    """AllowAddAnonymized sheet data structure."""


allow_add_anonymized_meta = sheet_meta._replace(
    isheet=IAllowAddAnonymized,
    schema_class=AllowAddAnonymizedSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheet and permission."""
    add_sheet_to_registry(allow_add_anonymized_meta, config.registry)
    # register free standing permission to validate permission names
    config.add_permission(ANONYMIZE_PERMISSION)
