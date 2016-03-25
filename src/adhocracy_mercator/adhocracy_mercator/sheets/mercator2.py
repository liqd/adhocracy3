"""Sheets for Mercator 2 proposals."""
from colander import Length
from colander import OneOf
from colander import drop
from colander import required
from colander import Invalid
from colander import Range

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import CurrencyAmount
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import ISOCountryCode
from adhocracy_core.schema import Integer
from adhocracy_core.schema import Reference
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import Text
from adhocracy_core.schema import URL
from adhocracy_core.schema import SequenceSchema
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.subresources import ISubResources


class IUserInfo(ISheet):
    """Marker interface for information about the proposal submitter."""


class UserInfoSchema(MappingSchema):
    """Information about the proposal submitter."""

    first_name = SingleLine(missing=required)
    last_name = SingleLine(missing=required)

userinfo_meta = sheet_meta._replace(isheet=IUserInfo,
                                    schema_class=UserInfoSchema)


class IOrganizationInfo(ISheet):
    """Marker interface for organizational information."""


class OrganizationStatusEnum(SingleLine):
    """Enum of organizational statuses."""

    default = 'other'
    missing = required
    validator = OneOf(['registered_nonprofit',
                       'planned_nonprofit',
                       'support_needed',
                       'other',
                       ])


class OrganizationInfoSchema(MappingSchema):
    """Data structure for organizational information."""

    name = SingleLine(missing=drop)
    validator= OneOf(['registered_nonprofit',
                      'planned_nonprofit',
                      'support_needed',
                      'other',
                      ])

    city = SingleLine(missing=drop)
    country = ISOCountryCode(missing=drop)
    help_request = Text(validator=Length(max=300))
    registration_date = DateTime(missing=drop, default=None)
    website = URL(missing=drop)
    status = OrganizationStatusEnum(missing=required)
    status_other = Text(validator=Length(max=300))

    def validator(self, node, value):
        """Extra validation depending on the status of the organisation.

        Make `status_other` required if `status` == `other` and
        `help_request` required if `status` == `support_needed`.
        """
        status = value.get('status', None)
        if status == 'support_needed':
            if not value.get('help_request', None):
                help_request = node['help_request']
                raise Invalid(
                    help_request,
                    msg='Required iff status == support_needed')
        elif status == 'other':
            if not value.get('status_other', None):
                status_other = node['status_other']
                raise Invalid(status_other,
                                       msg='Required iff status == other')


organizationinfo_meta = sheet_meta._replace(
    isheet=IOrganizationInfo,
    schema_class=OrganizationInfoSchema)


class IPitch(ISheet):
    """Marker interface for the pitch."""


class PitchSchema(MappingSchema):
    pitch = Text(missing=required,
                 validator=Length(min=3, max=500))


pitch_meta = sheet_meta._replace(
    isheet=IPitch, schema_class=PitchSchema)


class IPartners(ISheet):
    """Marker interface for the partner description."""


class PartnersSchema(MappingSchema):
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


class TopicEnum(SingleLine):
    """Enum of topic domains."""

    default = 'other'
    missing = required
    validator = OneOf(['democracy_and_participation',
                                'arts_and_cultural_activities',
                                'environment',
                                'social_inclusion',
                                'migration',
                                'communities',
                                'urban_development',
                                'education',
                                'other',
                                ])


class TopicEnums(SequenceSchema):
    """List of TopicEnums."""

    missing = required
    topics = TopicEnum()


class ITopic(ISheet):
    """Marker interface for the topic (ex: democracy, art, environment etc)."""


class TopicSchema(MappingSchema):
    topic = TopicEnums(validator=Length(min=1, max=2))
    topic_other = Text()

    def validator(self, node: SchemaNode, value: dict):
        """Extra validation depending on the status of the topic."""
        topics = value.get('topic', [])
        if 'other' in topics:
            if not value.get('topic_other', None):
                raise Invalid(node['topic_other'],
                                       msg='Required if "other" in topic')
        if _has_duplicates(topics):
            raise Invalid(node['topic'],
                                   msg='Duplicates are not allowed')


def _has_duplicates(iterable: list) -> bool:
    return len(iterable) != len(set(iterable))


topic_meta = sheet_meta._replace(
    isheet=ITopic,
    schema_class=TopicSchema)


class IDuration(ISheet):
    """Marker interface for the duration."""


class DurationSchema(MappingSchema):
    duration = Integer(missing=required)


duration_meta = sheet_meta._replace(
    isheet=IDuration,
    schema_class=DurationSchema)


class ILocation(ISheet):
    """Marker interface for the location."""


class LocationSchema(MappingSchema):
    location = SingleLine()
    is_online = Boolean()
    has_link_to_ruhr = Boolean(missing=required, default=False)
    link_to_ruhr = Text()

    def validator(self, node, value):
        """Extra validation depending on the status of the location.

        Make `link_to_ruhr` required if `has_link_to_ruhr` == `True`.
        """
        has_link_to_ruhr = value.get('has_link_to_ruhr', None)
        if has_link_to_ruhr:
            if not value.get('link_to_ruhr', None):
                link_to_ruhr = node['link_to_ruhr']
                raise Invalid(
                    link_to_ruhr,
                    msg='Required iff has_link_to_ruhr == True')


location_meta = sheet_meta._replace(
    isheet=ILocation,
    schema_class=LocationSchema,
)


class IStatus(ISheet):
    """Marker interface for the project status."""


class ProjectStatusEnum(SingleLine):
    """Enum of organizational statuses."""

    default = 'other'
    missing = required
    validator = OneOf(['starting',
                       'developing',
                       'scaling',
                       'other',
                       ])


class StatusSchema(MappingSchema):
    status = ProjectStatusEnum(missing=required)


status_meta = sheet_meta._replace(
    isheet=IStatus,
    schema_class=StatusSchema,
)


class IChallenge(ISheet):
    """Marker interface for the challenge in the road to impact section."""


class ChallengeSchema(MappingSchema):
    """Datastruct for the challenge field."""

    challenge = Text(missing=required,
                     validator=Length(min=3, max=500))

challenge_meta = sheet_meta._replace(
    isheet=IChallenge,
    schema_class=ChallengeSchema,
)


class IGoal(ISheet):
    """Marker interface for the 'aiming for' in the road to impact section."""


class GoalSchema(MappingSchema):
    """Datastruct for the goal."""

    goal = Text(missing=required,
                validator=Length(min=3, max=500))

goal_meta = sheet_meta._replace(
    isheet=IGoal,
    schema_class=GoalSchema,
)


class IPlan(ISheet):
    """Marker interface for the 'plan' in the road to impact section."""


class PlanSchema(MappingSchema):
    """Datastruct for the challenge field."""

    plan = Text(missing=required,
                validator=Length(min=3, max=800))

plan_meta = sheet_meta._replace(
    isheet=IPlan,
    schema_class=PlanSchema,
)


class ITarget(ISheet):
    """Marker interface for the 'target' in the road to impact section."""


class TargetSchema(MappingSchema):
    """Datastruct for the challenge field."""

    target = Text(missing=required,
                  validator=Length(min=3, max=500))

target_meta = sheet_meta._replace(
    isheet=ITarget,
    schema_class=TargetSchema,
)


class ITeam(ISheet):
    """Marker interface for the 'team' in the road to impact section."""


class TeamSchema(MappingSchema):
    """Datastruct for the challenge field."""

    team = Text(missing=required,
                validator=Length(min=3, max=800))

team_meta = sheet_meta._replace(
    isheet=ITeam,
    schema_class=TeamSchema,
)


class IExtraInfo(ISheet):
    """Marker interface for the 'extrainfo' in the road to impact section."""


class ExtraInfoSchema(MappingSchema):
    """Datastruct for the extra info field."""

    extrainfo = Text(missing=drop,
                     validator=Length(min=3, max=500))

extrainfo_meta = sheet_meta._replace(
    isheet=IExtraInfo,
    schema_class=ExtraInfoSchema,
)


class IConnectionCohesion(ISheet):
    """Marker iface for 'connection and cohesion' in the selection criteria."""


class ConnectionCohesionSchema(MappingSchema):
    """Datastruct for the connection and cohesion field."""

    connection_cohesion = Text(missing=required,
                               validator=Length(min=3, max=500))

connectioncohesion_meta = sheet_meta._replace(
    isheet=IConnectionCohesion,
    schema_class=ConnectionCohesionSchema,
)


class IDifference(ISheet):
    """Marker interface for the 'difference' in the selection section."""


class DifferenceSchema(MappingSchema):
    """Datastruct for the challenge field."""

    difference = Text(missing=required,
                      validator=Length(min=3, max=500))

difference_meta = sheet_meta._replace(
    isheet=IDifference,
    schema_class=DifferenceSchema,
)


class IPracticalRelevance(ISheet):
    """Marker for the 'practical relevance' in the selection criteria."""


class PracticalRelevanceSchema(MappingSchema):
    """Datastruct for the challenge field."""

    practicalrelevance = Text(missing=required,
                              validator=Length(min=3, max=500))

practicalrelevance_meta = sheet_meta._replace(
    isheet=IPracticalRelevance,
    schema_class=PracticalRelevanceSchema,
)


class IFinancialPlanning(ISheet):
    """Marker interface for the financial planning."""


class FinancialPlanningSchema(MappingSchema):
    budget = CurrencyAmount(missing=required)
    requested_funding = CurrencyAmount(missing=required,
                                       validator=Range(min=1, max=50000))
    major_expenses = Text(missing=required)


class IExtraFunding(ISheet):
    """Marker interface for the 'other sources of income' fie."""


class ExtraFundingSchema(MappingSchema):
    other_sources = Text(missing='')
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


class HeardFromEnum(SingleLine):
    """Enum of organizational statuses."""

    default = 'other'
    missing = required
    validator = OneOf(['personal_contact',
                       'website',
                       'facebook',
                       'twitter',
                       'newsletter',
                       'other',
                       ])


class HeardFromEnums(SequenceSchema):
    """List of HeardFromEnums."""

    missing = required
    heard_froms = HeardFromEnum()


class CommunitySchema(MappingSchema):
    expected_feedback = Text(missing=drop)
    heard_froms = HeardFromEnums(validator=Length(min=1))
    heard_from_other = Text()

    def validator(self, node: SchemaNode, value: dict):
        """Extra validation depending on the status of the heard froms."""
        heard_froms = value.get('heard_froms', [])
        if 'other' in heard_froms:
            if not value.get('heard_from_other', None):
                raise Invalid(
                    node['heard_from_other'],
                    msg='Required if "other" in heard_froms')
        if _has_duplicates(heard_froms):
            raise Invalid(node['heard_froms'],
                                   msg='Duplicates are not allowed')

community_meta = sheet_meta._replace(
    isheet=ICommunity,
    schema_class=CommunitySchema,
)


class IWinnerInfo(ISheet):
    """Marker interface for the winner information."""


class WinnerInfoSchema(MappingSchema):
    funding = Integer()

winnerinfo_meta = sheet_meta._replace(
    isheet=IWinnerInfo,
    schema_class=WinnerInfoSchema,
    permission_view='view_mercator2_winnerinfo',
    permission_edit='edit_mercator2_winnerinfo',
)


class IMercatorSubResources(ISubResources):
    """Marker interface for commentable subresources of MercatorProposal."""


class PitchReference(SheetToSheet):
    """Reference to pitch."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'pitch'
    target_isheet = IPitch


class PartnersReference(SheetToSheet):
    """Reference to partners."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'partners'
    target_isheet = IPartners


class DurationReference(SheetToSheet):
    """Reference to duration."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'duration'
    target_isheet = IDuration


class ChallengeReference(SheetToSheet):
    """Reference to challenge."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'challenge'
    target_isheet = IChallenge


class GoalReference(SheetToSheet):
    """Reference to goal."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'goal'
    target_isheet = IGoal


class PlanReference(SheetToSheet):
    """Reference to plan."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'plan'
    target_isheet = IPlan


class TargetReference(SheetToSheet):
    """Reference to target."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'target'
    target_isheet = ITarget


class TeamReference(SheetToSheet):
    """Reference to team."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'team'
    target_isheet = ITeam


class ExtraInfoReference(SheetToSheet):
    """Reference to extrainfo."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'extrainfo'
    target_isheet = IExtraInfo


class ConnectionCohesionReference(SheetToSheet):
    """Reference to connectioncohesion."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'connectioncohesion'
    target_isheet = IConnectionCohesion


class DifferenceReference(SheetToSheet):
    """Reference to difference."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'difference'
    target_isheet = IDifference


class PracticalRelevanceReference(SheetToSheet):
    """Reference to practical relevance."""

    source_isheet = IMercatorSubResources
    source_isheet_field = 'practicalrelevance'
    target_isheet = IPracticalRelevance


class MercatorSubResourcesSchema(MappingSchema):
    """Subresources of mercator."""

    pitch = Reference(reftype=PitchReference)
    partners = Reference(reftype=PartnersReference)
    duration = Reference(reftype=DurationReference)
    challenge = Reference(reftype=ChallengeReference)
    goal = Reference(reftype=GoalReference)
    plan = Reference(reftype=PlanReference)
    target = Reference(reftype=TargetReference)
    team = Reference(reftype=TeamReference)
    extrainfo = Reference(reftype=ExtraInfoReference)
    connectioncohesion = Reference(reftype=ConnectionCohesionReference)
    difference = Reference(reftype=DifferenceReference)
    practicalrelevance = Reference(reftype=PracticalRelevanceReference)


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
    add_sheet_to_registry(challenge_meta, config.registry)
    add_sheet_to_registry(goal_meta, config.registry)
    add_sheet_to_registry(plan_meta, config.registry)
    add_sheet_to_registry(target_meta, config.registry)
    add_sheet_to_registry(team_meta, config.registry)
    add_sheet_to_registry(extrainfo_meta, config.registry)
    add_sheet_to_registry(connectioncohesion_meta, config.registry)
    add_sheet_to_registry(difference_meta, config.registry)
    add_sheet_to_registry(practicalrelevance_meta, config.registry)
    add_sheet_to_registry(financialplanning_meta, config.registry)
    add_sheet_to_registry(extra_funding_meta, config.registry)
    add_sheet_to_registry(community_meta, config.registry)
    add_sheet_to_registry(winnerinfo_meta, config.registry)
    add_sheet_to_registry(mercator_subresources_meta, config.registry)
