"""Rate sheet."""
from pyramid.traversal import resource_path
from substanced.util import find_catalog
from zope.interface import implementer
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import IPredicateSheet
from adhocracy_core.interfaces import IPostPoolSheet
from adhocracy_core.interfaces import IRateValidator
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets.tags import filter_by_tag
from adhocracy_core.schema import Integer
from adhocracy_core.schema import Reference
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.schema import PostPoolMappingSchema
from adhocracy_core.schema import PostPool
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.utils import get_user


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

    """Reference from rate to rater."""

    source_isheet = IRate
    source_isheet_field = 'subject'
    target_isheet = ICanRate


class RateObjectReference(SheetToSheet):

    """Reference from rate to rated resource."""

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
        Validate the rate.

        This performs 3 checks:

        1. Validate that the subject is the user who is currently logged-in.

        2. Ensure that no other rate for the same subject/object combination
           exists, except predecessors of this version.

        3. Ask the validator registered for *object* whether *rate* is valid.
           In this way, `IRateable` subclasses can modify the range of allowed
           ratings by registering their own `IRateValidator` adapter.
        """
        request = node.bindings['request']
        self._validate_subject_is_current_user(node, value, request)
        self._ensure_rate_is_unique(node, value, request)
        self._query_registered_object_validator(node, value, request)

    def _validate_subject_is_current_user(self, node, value, request):
        user = get_user(request)
        if user is None or user != value['subject']:
            err = colander.Invalid(node)
            err['subject'] = 'Must be the currently logged-in user'
            raise err

    def _ensure_rate_is_unique(self, node, value, request):
        # Other rates with the same subject and object may occur below the
        # current context (earlier versions of the same rate item).
        # If they occur elsewhere, an error is thrown.
        adhocracy_catalog = find_catalog(request.context, 'adhocracy')
        index = adhocracy_catalog['reference']
        query = index.eq(IRate, 'subject', value['subject'])
        query &= index.eq(IRate, 'object', value['object'])
        system_catalog = find_catalog(request.context, 'system')
        path_index = system_catalog['path']
        query &= path_index.noteq(resource_path(request.context), depth=None)
        elements = query.execute(resolver=None)
        if elements:
            err = colander.Invalid(node)
            err['object'] = 'Another rate by the same user already exists'
            raise err

    def _query_registered_object_validator(self, node, value, request):
        registry = request.registry
        rate_validator = registry.getAdapter(value['object'], IRateValidator)
        if not rate_validator.validate(value['rate']):
            err = colander.Invalid(node)
            err['rate'] = rate_validator.helpful_error_message()
            raise err


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
    """
    Return aggregated values of referenceing :class:`IRate` resources.

    Only the LAST version of each rate is counted.
    """
    rates = get_sheet_field(resource, IRateable, 'rates')
    last_rates = filter_by_tag(rates, 'LAST')
    rate_sum = 0
    for rate in last_rates:
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
