"""Sheets for Mercator proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_metadata_defaults
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import Email
from adhocracy_core.schema import ISOCountryCode
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text


class IUserInfo(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for information about the proposal submitter."""


class IOrganizationInfo(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for organizational information."""


class IIntroduction(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the proposal introduction."""


class IDetails(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for proposal details."""


class IMotivation(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for the motivation behind the proposal."""


class IFinance(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for financial aspects."""


class IExtras(ISheet, ISheetReferenceAutoUpdateMarker):

    """Marker interface for additional fields."""


class UserInfoSchema(colander.MappingSchema):

    """Data structure for information about the proposal submitter."""

    personal_name = SingleLine(missing=colander.required)
    family_name = SingleLine()
    email = Email(missing=colander.required)


userinfo_meta = sheet_metadata_defaults._replace(isheet=IUserInfo,
                                                 schema_class=UserInfoSchema)


class StatusEnum(AdhocracySchemaNode):

    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['registered_nonprofit',
                                'planned_nonprofit',
                                'support_needed',
                                'other',
                                ])


class SizeEnum(AdhocracySchemaNode):

    """Enum of organization sizes."""

    schema_type = colander.String
    default = '0+'
    missing = colander.required
    validator = colander.OneOf(['0+', '5+', '10+', '20+', '50+'])


class OrganizationInfoSchema(colander.MappingSchema):

    """Data structure for organizational information."""

    name = SingleLine(missing=colander.required)
    email = Email(missing=colander.required)
    street_address = SingleLine(missing=colander.required)
    postcode = SingleLine(missing=colander.required)
    city = SingleLine(missing=colander.required)
    country = ISOCountryCode()
    status = StatusEnum()
    status_other = Text(validator=colander.Length(max=500))
    """Custom description for status == other."""
    # FIXME status_other must be non-empty if status=other, otherwise it must
    # be empty or null
    description = Text(validator=colander.Length(min=1, max=750))
    size = SizeEnum()
    cooperation_explanation = Text(validator=colander.Length(max=300))
    """Custom description for cooperation.
    Setting this value also means 'cooperation' == True in the frontend form.
    """

    def validator(self, node, value):
        """Make `status_other` required if `status` == `other`."""
        status = value.get('status', None)
        status_other = value.get('status_other', None)
        if status == 'other' and not status_other:
            status_other = node['status_other']
            raise colander.Invalid(status_other, msg='Required')


organizationinfo_meta = sheet_metadata_defaults._replace(
    isheet=IOrganizationInfo, schema_class=OrganizationInfoSchema)


class IntroductionSchema(colander.MappingSchema):

    """Data structure for the proposal introduction."""

    title = SingleLine(validator=colander.Length(min=1, max=100))
    teaser = Text(validator=colander.Length(min=1, max=300))
    # picture = AssetPath()


introduction_meta = sheet_metadata_defaults._replace(
    isheet=IIntroduction, schema_class=IntroductionSchema)


class DetailsSchema(colander.MappingSchema):

    """Data structure for for proposal details."""

    description = Text(validator=colander.Length(min=1, max=1000))
    location_is_city = Boolean()
    location_is_country = Boolean()
    location_is_town = Boolean()
    location_is_online = Boolean()
    location_is_linked_to_ruhr = Boolean()
    story = Text(validator=colander.Length(min=1, max=800))


details_meta = sheet_metadata_defaults._replace(isheet=IDetails,
                                                schema_class=DetailsSchema)


class MotivationSchema(colander.MappingSchema):

    """Data structure for the motivation behind the proposal."""

    outcome = Text(validator=colander.Length(min=1, max=800))
    steps = Text(validator=colander.Length(min=1, max=800))
    value = Text(validator=colander.Length(min=1, max=800))
    partners = Text(validator=colander.Length(min=1, max=800))


motivation_meta = sheet_metadata_defaults._replace(
    isheet=IMotivation, schema_class=MotivationSchema)


class FinanceSchema(colander.MappingSchema):

    """Data structure for financial aspects."""

    budget = CurrencyAmount(missing=colander.required)
    requested_funding = CurrencyAmount(missing=colander.required)
    granted = Boolean()
    # financial_plan = AssetPath()  # (2 Mb. max.)


finance_meta = sheet_metadata_defaults._replace(isheet=IFinance,
                                                schema_class=FinanceSchema)


class ExtrasSchema(colander.MappingSchema):

    """Data structure for additional fields."""

    # media = list of AssetPath()
    # categories = list of enum???
    experience = Text()
    heard_from_colleague = Boolean()
    heard_from_website = Boolean()
    heard_from_newsletter = Boolean()
    heard_from_facebook = Boolean()
    # There is no heard_from_elsewhere Boolean, since that automatically
    # follows iff heard_elsewhere is not empty
    heard_elsewhere = Text()


extras_meta = sheet_metadata_defaults._replace(isheet=IExtras,
                                               schema_class=ExtrasSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(userinfo_meta, config.registry)
    add_sheet_to_registry(organizationinfo_meta, config.registry)
    add_sheet_to_registry(introduction_meta, config.registry)
    add_sheet_to_registry(details_meta, config.registry)
    add_sheet_to_registry(motivation_meta, config.registry)
    add_sheet_to_registry(finance_meta, config.registry)
    add_sheet_to_registry(extras_meta, config.registry)
