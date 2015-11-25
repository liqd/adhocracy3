"""Sheets for Mercator 2 proposals."""
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Email
from adhocracy_core.schema import ISOCountryCode
from adhocracy_core.schema import Integer
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.schema import URL
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta


class IUserInfo(ISheet):
    """Marker interface for information about the proposal submitter."""


class UserInfoSchema(colander.MappingSchema):
    """Information about the proposal submitter."""

    first_name = SingleLine(missing=colander.required)
    last_name = SingleLine(missing=colander.required)

userinfo_meta = sheet_meta._replace(isheet=IUserInfo,
                                    schema_class=UserInfoSchema)


class IOrganizationInfo(ISheet):
    """Marker interface for organizational information."""


class OrganizationStatusEnum(AdhocracySchemaNode):
    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['registered_nonprofit',
                                'planned_nonprofit',
                                'support_needed',
                                'other',
                                ])


class OrganizationInfoSchema(colander.MappingSchema):
    """Data structure for organizational information."""

    name = SingleLine(missing=colander.required)
    city = SingleLine(missing=colander.required)
    country = ISOCountryCode(missing=colander.required)
    help_request = Text(validator=colander.Length(max=300))
    registration_date = DateTime(missing=colander.required, default=None)
    website = URL(missing=colander.drop)
    contact_email = Email(missing=colander.required)
    status = OrganizationStatusEnum(missing=colander.required)
    status_other = Text(validator=colander.Length(max=300))

    def validator(self, node, value):
        """Extra validation depending on the status of the organisation.

        Make `status_other` required if `status` == `other` and
        `help_request` required if `status` == `support_needed`.
        """
        status = value.get('status', None)
        if status == 'support_needed':
            if not value.get('help_request', None):
                help_request = node['help_request']
                raise colander.Invalid(
                    help_request,
                    msg='Required iff status == support_needed')
        elif status == 'other':
            if not value.get('status_other', None):
                status_other = node['status_other']
                raise colander.Invalid(status_other,
                                       msg='Required iff status == other')


organizationinfo_meta = sheet_meta._replace(
    isheet=IOrganizationInfo,
    schema_class=OrganizationInfoSchema)


class IPitch(ISheet):
    """Marker interface for the pitch."""


class PitchSchema(colander.MappingSchema):
    pitch = Text(missing=colander.required,
                 validator=colander.Length(min=3, max=100))


pitch_meta = sheet_meta._replace(
    isheet=IPitch, schema_class=PitchSchema)


class IPartners(ISheet):
    """Marker interface for the partner description."""


class PartnersSchema(colander.MappingSchema):
    has_partners = Boolean()
    partner1_name = SingleLine()
    partner1_website = URL()
    partner1_country = ISOCountryCode()
    partner2_name = SingleLine()
    partner2_website = URL()
    partner2_country = ISOCountryCode()
    partner3_name = SingleLine()
    partner3_website = URL()
    partner3_country = ISOCountryCode()
    other_partners = Text()


partners_meta = sheet_meta._replace(
    isheet=IPartners, schema_class=PartnersSchema)


class TopicEnum(AdhocracySchemaNode):
    """Enum of topic domains."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['democracy_and_participation',
                                'arts_and_cultural_activities',
                                'environment',
                                'social_inclusion',
                                'migration',
                                'communities',
                                'urban_development',
                                'education',
                                'other',
                                ])


class ITopic(ISheet):
    """Marker interface for the topic (ex: democracy, art, environment etc)."""


class TopicSchema(colander.MappingSchema):
    topic = TopicEnum(missing=colander.required)
    other = Text()

    def validator(self, node, value):
        """Extra validation depending on the status of the topic.

        Make `other` required if `topic` == `other`.
        """
        topic = value.get('topic', None)
        if topic == 'other':
            if not value.get('other', None):
                other = node['other']
                raise colander.Invalid(
                    other,
                    msg='Required iff topic == other')

topic_meta = sheet_meta._replace(
    isheet=ITopic,
    schema_class=TopicSchema)


class IDuration(ISheet):
    """Marker interface for the duration."""


class DurationSchema(colander.MappingSchema):
    duration = Integer(missing=colander.required)


duration_meta = sheet_meta._replace(
    isheet=IDuration,
    schema_class=DurationSchema)


class ILocation(ISheet):
    """Marker interface for the location."""


class LocationSchema(colander.MappingSchema):
    location = SingleLine(missing=colander.required)
    is_online = Boolean()
    has_link_to_ruhr = Boolean(missing=colander.required, default=False)
    link_to_ruhr = Text()

    def validator(self, node, value):
        """Extra validation depending on the status of the location.

        Make `link_to_ruhr` required if `has_link_to_ruhr` == `True`.
        """
        has_link_to_ruhr = value.get('has_link_to_ruhr', None)
        if has_link_to_ruhr:
            if not value.get('link_to_ruhr', None):
                link_to_ruhr = node['link_to_ruhr']
                raise colander.Invalid(
                    link_to_ruhr,
                    msg='Required iff has_link_to_ruhr == True')


location_meta = sheet_meta._replace(
    isheet=ILocation,
    schema_class=LocationSchema,
)


class IStatus(ISheet):
    """Marker interface for the project status."""


class ProjectStatusEnum(AdhocracySchemaNode):
    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['starting',
                                'developping',
                                'scaling',
                                'other',
                                ])


class StatusSchema(colander.MappingSchema):
    status = ProjectStatusEnum(missing=colander.required)


status_meta = sheet_meta._replace(
    isheet=IStatus,
    schema_class=StatusSchema,
)


class IRoadToImpact(ISheet):
    """Marker interface for the road to impact."""


class RoadToImpactSchema(colander.MappingSchema):
    challenge = Text(missing=colander.required,
                     validator=colander.Length(min=3, max=500))
    aim = Text(missing=colander.required,
               validator=colander.Length(min=3, max=500))
    plan = Text(missing=colander.required,
                validator=colander.Length(min=3, max=800))
    doing = Text(missing=colander.required,
                 validator=colander.Length(min=3, max=500))
    team = Text(missing=colander.required,
                validator=colander.Length(min=3, max=800))
    other = Text(missing=colander.required,
                 validator=colander.Length(min=3, max=500))


roadtoimpact_meta = sheet_meta._replace(
    isheet=IRoadToImpact,
    schema_class=RoadToImpactSchema,
)


class ISelectionCriteria(ISheet):
    """Marker interface for the selection criteria."""


class SelectionCriteriaSchema(colander.MappingSchema):
    connection_and_cohesion_europe = Text(
        missing=colander.required,
        validator=colander.Length(min=3, max=500))
    difference = Text(missing=colander.required,
                      validator=colander.Length(min=3, max=500))
    practical_relevance = Text(missing=colander.required,
                               validator=colander.Length(min=3, max=500))


selectioncriteria_meta = sheet_meta._replace(
    isheet=ISelectionCriteria,
    schema_class=SelectionCriteriaSchema,
)


class IFinancialPlanning(ISheet):
    """Marker interface for the financial planning."""


class FinancialPlanningSchema(colander.MappingSchema):
    budget = CurrencyAmount(missing=colander.required)
    requested_funding = CurrencyAmount(
        missing=colander.required,
        validator=colander.Range(min=1, max=50000))
    major_expenses = Text(missing=colander.required)


class IExtraFunding(ISheet):
    """Marker interface for the 'other sources of income' fie."""


class ExtraFundingSchema(colander.MappingSchema):
    other_sources = Text()
    secured = Boolean(default=False)


extra_funding_meta = sheet_meta._replace(
    isheet=IExtraFunding,
    schema_class=ExtraFundingSchema,
    permission_view='view_mercator2_extra_funding',
)


financialplanning_meta = sheet_meta._replace(
    isheet=IFinancialPlanning,
    schema_class=FinancialPlanningSchema,
)


class ICommunity(ISheet):
    """Marker interface for the community information."""


class HeardFromEnum(AdhocracySchemaNode):
    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['personal_contact',
                                'website',
                                'facebook',
                                'twitter',
                                'newsletter',
                                'other',
                                ])


class CommunitySchema(colander.MappingSchema):
    expected_feedback = Text(missing=colander.required)
    heard_from = HeardFromEnum(missing=colander.required)
    heard_from_other = Text()


community_meta = sheet_meta._replace(
    isheet=ICommunity,
    schema_class=CommunitySchema,
)


class IWinnerInfo(ISheet):
    """Marker interface for the winner information."""


class WinnerInfoSchema(colander.MappingSchema):
    explanation = Text()
    funding = Integer()

winnerinfo_meta = sheet_meta._replace(
    isheet=IWinnerInfo,
    schema_class=WinnerInfoSchema,
    permission_view='view_mercator2_winnerinfo',
    permission_edit='edit_mercator2_winnerinfo',
)


class IMercatorSubResources(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for commentable subresources of MercatorProposal."""


class PitchReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'pitch'
    target_isheet = IPitch


class PartnersReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'partners'
    target_isheet = IPartners


class DurationReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'duration'
    target_isheet = IDuration


class LocationReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'duration'
    target_isheet = ILocation


class RoadToImpactReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'road_to_impact'
    target_isheet = IStatus


class SelectionCriteriaReference(SheetToSheet):
    source_isheet = IMercatorSubResources
    source_isheet_field = 'selection_criteria'
    target_isheet = ISelectionCriteria


class MercatorSubResourcesSchema(colander.MappingSchema):
    pitch = Reference(reftype=PitchReference)
    partners = Reference(reftype=PartnersReference)
    duration = Reference(reftype=DurationReference)
    road_to_impact = Reference(reftype=RoadToImpactReference)
    selection_criteria = Reference(reftype=SelectionCriteriaReference)


mercator_subresources_meta = sheet_meta._replace(
    isheet=IMercatorSubResources,
    schema_class=MercatorSubResourcesSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(userinfo_meta, config.registry)
    add_sheet_to_registry(organizationinfo_meta, config.registry)
    add_sheet_to_registry(pitch_meta, config.registry)
    add_sheet_to_registry(partners_meta, config.registry)
    add_sheet_to_registry(topic_meta, config.registry)
    add_sheet_to_registry(duration_meta, config.registry)
    add_sheet_to_registry(location_meta, config.registry)
    add_sheet_to_registry(status_meta, config.registry)
    add_sheet_to_registry(roadtoimpact_meta, config.registry)
    add_sheet_to_registry(selectioncriteria_meta, config.registry)
    add_sheet_to_registry(financialplanning_meta, config.registry)
    add_sheet_to_registry(extra_funding_meta, config.registry)
    add_sheet_to_registry(community_meta, config.registry)
    add_sheet_to_registry(winnerinfo_meta, config.registry)
    add_sheet_to_registry(mercator_subresources_meta, config.registry)
