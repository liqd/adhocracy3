"""Rate sheet."""
from zope.interface import implementer
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IPredicateSheet
from adhocracy_core.interfaces import IPostPoolSheet
from adhocracy_core.interfaces import IRateValidator
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import Integer
from adhocracy_core.schema import Reference
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.schema import PostPoolMappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.utils import get_sheet_field


class IRate(IPredicateSheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the rate sheet."""


class IRateable(IPostPoolSheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for resources that can be rated."""


@implementer(IRateValidator)
class RateableRateValidator:

    """
    Validator for rates about IRateable.

    The following values are allowed:

      * 1: pro
      * 0: neutral
      * -1: contra
    """

    _allowed_values = (1, 0, -1)

    def __init__(self, context):
        self.context = context

    def validate(self, rate: int) -> bool:
        return rate in self._allowed_values

    def helpful_error_message(self) -> str:
        return 'rate must be one of {}'.format(self._allowed_values)


class ILikeable(IRateable):

    """IRateable subclass that restricts the set of allowed values."""


@implementer(IRateValidator)
class LikeableRateValidator(RateableRateValidator):

    """
    Validator for rates about ILikeable.

    The following values are allowed:

      * 1: like
      * 0: neutral/no vote
    """

    _allowed_values = (1, 0)


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

    """Rate sheet data structure."""

    subject = Reference(reftype=RateSubjectReference)
    object = Reference(reftype=RateObjectReference)
    rate = Integer()

    def validator(self, node, value):
        """
        Ask the validator registered for *object* whether *rate* is valid.

        In this way, `IRateable` subclasses can modify the range of allowed
        ratings by registering their own `IRateValidator` adapter.
        """
        registry = node.bindings['request'].registry
        validator = registry.getAdapter(value['object'], IRateValidator)
        if not validator.validate(value['rate']):
            rate_node = node['rate']
            raise colander.Invalid(rate_node,
                                   msg=validator.helpful_error_message())


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

    rates = UniqueReferences(readonly=True,
                             backref=True,
                             reftype=RateObjectReference)
    post_pool = PostPool(iresource_or_service_name='rates')


rateable_meta = sheet_metadata_defaults._replace(
    isheet=IRateable,
    schema_class=RateableSchema,
    editable=False,
    creatable=False,
)


likeable_meta = rateable_meta._replace(
    isheet=ILikeable,
)


def index_rate(resource, default):
    """Return the value of field name `rate` for :class:`IRate` resources."""
    # FIXME?: can we pass the registry to get_sheet_field her?
    rate = get_sheet_field(resource, IRate, 'rate')
    return rate


def index_rates(resource, default):
    """Return aggregated values of referenceing :class:`IRate` resources."""
    rates = get_sheet_field(resource, IRateable, 'rates')
    rate_sum = 0
    for rate in rates:
        value = get_sheet_field(rate, IRate, 'rate')
        rate_sum += value
    return rate_sum


def includeme(config):
    """Register sheets, adapters and index views."""
    add_sheet_to_registry(rate_meta, config.registry)
    add_sheet_to_registry(can_rate_meta, config.registry)
    add_sheet_to_registry(rateable_meta, config.registry)
    add_sheet_to_registry(likeable_meta, config.registry)
    config.registry.registerAdapter(RateableRateValidator,
                                    (IRateable,),
                                    IRateValidator)
    config.registry.registerAdapter(LikeableRateValidator,
                                    (ILikeable,),
                                    IRateValidator)
    config.add_indexview(index_rate,
                         catalog_name='adhocracy',
                         index_name='rate',
                         context=IRate)
    config.add_indexview(index_rates,
                         catalog_name='adhocracy',
                         index_name='rates',
                         context=IRateable)
