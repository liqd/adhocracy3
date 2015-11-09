"""Mercator 2 proposal."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources.logbook import add_logbook_service
from adhocracy_core.resources.proposal import IProposal
from adhocracy_core.resources.simple import simple_meta
from adhocracy_core.sheets.comment import ICommentable
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.image import IImageReference
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.rate import add_ratesservice
from adhocracy_core.resources.badge import add_badge_assignments_service

import adhocracy_mercator.sheets.mercator2
import adhocracy_core.sheets


class IPitch(ISimple):
    """Proposal's pitch."""


pitch_meta = simple_meta._replace(
    content_name='Pitch',
    iresource=IPitch,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='pitch',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IPitch,
        adhocracy_core.sheets.description.IDescription,
        adhocracy_core.sheets.comment.ICommentable),
)


class IPartners(ISimple):
    """Proposal's partners."""


partners_meta = simple_meta._replace(
    content_name='Partners',
    iresource=IPartners,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='partners',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IPartners,
        adhocracy_core.sheets.comment.ICommentable),
)


class IDuration(ISimple):
    """Duration."""

duration_meta = simple_meta._replace(
    content_name='duration',
    iresource=IDuration,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='duration',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IDuration,
        adhocracy_core.sheets.comment.ICommentable),
)


class IRoadToImpact(ISimple):
    """Road to impact."""

road_to_impact_meta = simple_meta._replace(
    content_name='road_to_impact',
    iresource=IRoadToImpact,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='road_to_impact',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IRoadToImpact,
        adhocracy_core.sheets.comment.ICommentable),
)


class ISelectionCriteria(ISimple):
    """Road to impact."""

selection_criteria_meta = simple_meta._replace(
    content_name='selection_criteria',
    iresource=ISelectionCriteria,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='selection_criteria',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.ISelectionCriteria,
        adhocracy_core.sheets.comment.ICommentable),
)


class IMercatorProposal(IProposal):
    """Mercator 2 proposal. Not versionable."""


proposal_meta = proposal.proposal_meta._replace(
    content_name='MercatorProposal2',
    iresource=IMercatorProposal,
    element_types=(IPitch,
                   IPartners,
                   IRoadToImpact,
                   ISelectionCriteria),
    after_creation=(
        add_commentsservice,
        add_ratesservice,
        add_badge_assignments_service,
        add_logbook_service,)
)._add(extended_sheets=
       (ITitle,
        IDescription,
        ICommentable,
        IRateable,
        IImageReference,
        adhocracy_mercator.sheets.mercator2.IMercatorSubResources,
        adhocracy_mercator.sheets.mercator2.IUserInfo,
        adhocracy_mercator.sheets.mercator2.IOrganizationInfo,
        adhocracy_mercator.sheets.mercator2.ITopic,
        adhocracy_mercator.sheets.mercator2.ILocation,
        adhocracy_mercator.sheets.mercator2.IStatus,
        adhocracy_mercator.sheets.mercator2.IFinancialPlanning,
        adhocracy_mercator.sheets.mercator2.IExtraFunding,
        adhocracy_mercator.sheets.mercator2.ICommunity,
        adhocracy_mercator.sheets.mercator2.IWinnerInfo))


class IProcess(process.IProcess):
    """Mercator 2 participation process."""


process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=(IMercatorProposal,
                   ),
    workflow_name='mercator2'
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(pitch_meta, config)
    add_resource_type_to_registry(partners_meta, config)
    add_resource_type_to_registry(duration_meta, config)
    add_resource_type_to_registry(road_to_impact_meta, config)
    add_resource_type_to_registry(selection_criteria_meta, config)
