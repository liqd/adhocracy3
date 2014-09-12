"""Rating sheet."""
from enum import Enum

import colander

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IPostPoolSheet
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import IItem
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.schema import Reference
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.schema import PostPoolMappingSchema
from adhocracy.schema import PostPool


class RatingValue(Enum):
    contra = -1
    neutral = 0
    pro = 1


class IRating(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the rating sheet."""


class IRateable(IPostPoolSheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that can be rated."""


class ICanRate(ISheet):

    """Marker interface for resources that can rate."""


class RatingSubjectReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IRating
    source_isheet_field = 'subject'
    target_isheet = ICanRate


class RatingTargetReference(SheetToSheet):

    """Reference from comment version to the commented-on item version."""

    source_isheet = IRating
    source_isheet_field = 'target'
    target_isheet = IRateable


class RatingSchema(colander.MappingSchema):

    """Rating sheet data structure.

    `value`:  Integer
    """

    subject = Reference(reftype=RatingSubjectReference)
    target = Reference(reftype=RatingTargetReference)
    value = colander.Integer()


rating_meta = sheet_metadata_defaults._replace(isheet=IRating,
                                               schema_class=RatingSchema,
                                               create_mandatory=True)


class CanRateSchema(colander.MappingSchema):

    """CanRate sheet data structure."""


can_rate_meta = sheet_metadata_defaults._replace(isheet=ICanRate,
                                                 schema_class=CanRateSchema)


class RateableSchema(PostPoolMappingSchema):

    """Commentable sheet data structure.

    `post_pool`: Pool to post new :class:`adhocracy_sample.resource.IRating`.
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
    add_sheet_to_registry(rating_meta, config.registry)
    add_sheet_to_registry(can_rate_meta, config.registry)
    add_sheet_to_registry(rateable_meta, config.registry)
