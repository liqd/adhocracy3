"""Polarization sheet."""
import colander

from adhocracy_core.sheets import sheet_meta
from adhocracy_core.interfaces import IPredicateSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.interfaces import ISheet
from adhocracy_core.schema import Reference as ReferenceSchema
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import PostPool


class IPolarization(IPredicateSheet):

    """Marker interface for the polarization sheet."""


class IPolarizable(ISheet):

    """Marker interface for resources than can be polarized."""


class ICanPolarize(ISheet):

    """Marker interface for resources that can rate."""


class Position(AdhocracySchemaNode):

    """Schema node for the side (pro or contra)."""

    schema_type = colander.String
    missing = colander.drop
    default = 'pro'
    validator = colander.OneOf(['pro', 'contra']),


class PolarizationSubjectReference(SheetToSheet):

    """Reference from polarization to polarizer."""

    source_isheet = IPolarization
    source_isheet_field = 'subject'
    target_isheet = ICanPolarize


class PolarizationObjectReference(SheetToSheet):

    """Reference from polarization to polarized resource."""

    source_isheet = IPolarization
    source_isheet_field = 'object'
    target_isheet = IPolarizable


class PolarizationSchema(colander.MappingSchema):

    """
    Polarizable sheet data structure.

    `position`: the position in the debate, 'pro' or 'contra'.
    """

    subject = ReferenceSchema(reftype=PolarizationSubjectReference)
    object = ReferenceSchema(reftype=PolarizationObjectReference)
    position = Position()

polarization_meta = sheet_meta._replace(isheet=IPolarization,
                                        schema_class=PolarizationSchema,
                                        create_mandatory=True)


class CanPolarizeSchema(colander.MappingSchema):

    """CanPolarize sheet data structure."""


can_rate_meta = sheet_meta._replace(isheet=ICanPolarize,
                                    schema_class=CanPolarizeSchema)


class PolarizableSchema(colander.MappingSchema):

    """Polarizable sheet data structure.

    `post_pool`: Pool to post :class:`adhocracy_core.resource.IPolarization`.
    """

    polarizations = UniqueReferences(readonly=True,
                                     backref=True,
                                     reftype=PolarizationObjectReference)
    post_pool = PostPool(iresource_or_service_name='polarizations')


polarizable_meta = sheet_meta._replace(
    isheet=IPolarizable,
    schema_class=PolarizableSchema,
    editable=True,
    creatable=True,
    create_mandatory=True
)


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(polarizable_meta, config.registry)
