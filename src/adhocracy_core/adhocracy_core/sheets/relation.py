"""Sheets for statements about relations between process content/comments."""
from colander import drop
from colander import OneOf

from adhocracy_core.interfaces import IPredicateSheet
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta


class IPolarization(IPredicateSheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for the polarization sheet."""


class IPolarizable(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for resources than can be polarized."""


class ICanPolarize(ISheet):
    """Marker interface for resources that can polarize."""


class Position(SingleLine):
    """Schema node for the side (pro or contra)."""

    missing = drop
    default = 'pro'
    validator = OneOf(['pro', 'contra'])


class PolarizationSubjectReference(SheetToSheet):
    """Reference from polarization to polarize."""

    source_isheet = IPolarization
    source_isheet_field = 'subject'
    target_isheet = ICanPolarize


class PolarizationObjectReference(SheetToSheet):
    """Reference from polarization to polarized resource."""

    source_isheet = IPolarization
    source_isheet_field = 'object'
    target_isheet = IPolarizable


class PolarizationSchema(MappingSchema):
    """Polarizable sheet data structure.

    `position`: the position in the debate, 'pro' or 'contra'.
    """

    subject = Reference(reftype=PolarizationSubjectReference)
    object = Reference(reftype=PolarizationObjectReference)
    position = Position()

polarization_meta = sheet_meta._replace(isheet=IPolarization,
                                        schema_class=PolarizationSchema,
                                        create_mandatory=True)


class CanPolarizeSchema(MappingSchema):
    """CanPolarize sheet data structure."""

    polarization = Reference(reftype=PolarizationSubjectReference,
                             backref=True,
                             readonly=True,)

can_polarize_meta = sheet_meta._replace(isheet=ICanPolarize,
                                        schema_class=CanPolarizeSchema)


class PolarizableSchema(MappingSchema):
    """Polarizable sheet data structure.

    `post_pool`: Pool to post :class:`adhocracy_core.resource.IPolarization`.
    """

    polarizations = UniqueReferences(readonly=True,
                                     backref=True,
                                     reftype=PolarizationObjectReference)
    post_pool = PostPool(iresource_or_service_name='relations')


polarizable_meta = sheet_meta._replace(
    isheet=IPolarizable,
    schema_class=PolarizableSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(polarization_meta, config.registry)
    add_sheet_to_registry(polarizable_meta, config.registry)
    add_sheet_to_registry(can_polarize_meta, config.registry)
