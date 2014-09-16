"""Rate sheet."""
import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IPredicateSheet
from adhocracy.interfaces import IPostPoolSheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import IItem
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import Reference
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.schema import PostPoolMappingSchema
from adhocracy.schema import PostPool
from adhocracy.schema import Rate


class IRate(IPredicateSheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the rate sheet."""


class IRateable(IPostPoolSheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that can be rated."""


class ICanRate(ISheet):

    """Marker interface for resources that can rate."""


class RateSubjectReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IRate
    source_isheet_field = 'subject'
    target_isheet = ICanRate


class RateObjectReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IRate
    source_isheet_field = 'object'
    target_isheet = IRateable


class RateSchema(colander.MappingSchema):

    """Rate sheet data structure.

    `rate`: 1, 0, or -1
    """

    subject = Reference(reftype=RateSubjectReference)
    object = Reference(reftype=RateObjectReference)
    rate = Rate()


rate_meta = sheet_metadata_defaults._replace(isheet=IRate,
                                             schema_class=RateSchema,
                                             create_mandatory=True)


class CanRateSchema(colander.MappingSchema):

    """CanRate sheet data structure."""


can_rate_meta = sheet_metadata_defaults._replace(isheet=ICanRate,
                                                 schema_class=CanRateSchema)


class RateableSchema(PostPoolMappingSchema):

    """Commentable sheet data structure.

    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IRate`.
    """

    post_pool = PostPool(iresource_or_service_name=IItem)


rateable_meta = sheet_metadata_defaults._replace(
    isheet=IRateable,
    schema_class=RateableSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(rate_meta, config.registry)
    add_sheet_to_registry(can_rate_meta, config.registry)
    add_sheet_to_registry(rateable_meta, config.registry)
