"""Activity sheet."""
from colander import OneOf

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import ActivityType
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.principal import IUserBasic


class IActivity(ISheet):
    """Marker interface for the activity sheet."""


class SubjectReference(SheetToSheet):
    """Reference from an acticity to its subject."""

    source_isheet = IActivity
    source_isheet_field = 'subject'
    target_isheet = IUserBasic


class ObjectReference(SheetToSheet):
    """Reference from the acticity to its subject."""

    source_isheet = IActivity
    source_isheet_field = 'object'
    target_isheet = ISheet


class TargetReference(SheetToSheet):
    """Reference from the activity to its target."""

    source_isheet = IActivity
    source_isheet_field = 'target'
    target_isheet = ISheet


class ActivitySchema(MappingSchema):
    """Activity entry."""

    subject = Reference(reftype=SubjectReference)
    type = SingleLine(validator=OneOf(
        [activity_type.value for activity_type in ActivityType]))
    object = Reference(reftype=ObjectReference)
    target = Reference(reftype=TargetReference)
    name = SingleLine()
    published = DateTime()


activity_meta = sheet_meta._replace(
    isheet=IActivity,
    schema_class=ActivitySchema,
    editable=False,
    creatable=True,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(activity_meta, config.registry)
