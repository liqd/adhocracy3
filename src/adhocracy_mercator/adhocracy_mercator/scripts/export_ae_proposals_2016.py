"""Export advocate europe 2016 proposal.

This is registered as console script 'export_ae_proposals_2016'
in setup.py.
"""

import argparse
import csv
import inspect
import textwrap
from functools import partial

from pyramid.registry import Registry
from pyramid.paster import bootstrap
from substanced.util import find_service
from adhocracy_core.utils import create_filename

from adhocracy_core.utils import get_sheet_field
from adhocracy_core.interfaces import search_query

from pyramid.traversal import resource_path

from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_mercator.resources.mercator2 import IMercatorProposal
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_mercator.sheets.mercator2 import IUserInfo
from adhocracy_mercator.sheets.mercator2 import IOrganizationInfo
from adhocracy_mercator.sheets.mercator2 import IPitch
from adhocracy_mercator.sheets.mercator2 import IMercatorSubResources
from adhocracy_mercator.sheets.mercator2 import IPartners
from adhocracy_mercator.sheets.mercator2 import ITopic
from adhocracy_mercator.sheets.mercator2 import IDuration
from adhocracy_mercator.sheets.mercator2 import ILocation
from adhocracy_mercator.sheets.mercator2 import IStatus
from adhocracy_mercator.sheets.mercator2 import IChallenge
from adhocracy_mercator.sheets.mercator2 import IGoal
from adhocracy_mercator.sheets.mercator2 import IPlan
from adhocracy_mercator.sheets.mercator2 import ITarget
from adhocracy_mercator.sheets.mercator2 import ITeam
from adhocracy_mercator.sheets.mercator2 import IExtraInfo
from adhocracy_mercator.sheets.mercator2 import IConnectionCohesion
from adhocracy_mercator.sheets.mercator2 import IDifference
from adhocracy_mercator.sheets.mercator2 import IPracticalRelevance
from adhocracy_mercator.sheets.mercator2 import IFinancialPlanning
from adhocracy_mercator.sheets.mercator2 import IExtraFunding
from adhocracy_mercator.sheets.mercator2 import ICommunity


def normalize_text(s: str) -> str:
    """Normalize text to put it in CVS."""
    return s.replace(';', '')


def export_proposals():
    """Export all proposals from database and write them to csv file."""
    doc = textwrap.dedent(inspect.getdoc(export_proposals))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('config')
    args = parser.parse_args()

    env = bootstrap(args.config)

    root = env['root']
    registry = env['registry']
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=IMercatorProposal,
                                  resolve=True,
                                  )
    proposals = catalogs.search(query).elements

    filename = create_filename(directory='./var/export',
                               prefix='ae-2016-proposals',
                               suffix='.csv')
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)

    wr.writerow(['URL',
                 'Creation date',
                 'Title',
                 'Creator name',
                 'Creator email',
                 'First name',
                 'Last name',
                 'Organisation name',
                 'Organisation city',
                 'Organisation country',
                 'Organisation help request',
                 'Organisation registration date',
                 'Organisation website',
                 'Organisation status',
                 'Organisation status other',
                 'Pitch',
                 'Partner1 name',
                 'Partner1 website',
                 'Partner1 country',
                 'Partner2 name',
                 'Partner2 website',
                 'Partner2 country',
                 'Partner3 name',
                 'Partner3 website',
                 'Partner3 country',
                 'Other partners',
                 'Topics',
                 'Topic other',
                 'Duration',
                 'Location',
                 'Is online',
                 'Link to Ruhr',
                 'Status',
                 'Challenge',
                 'Goal',
                 'Plan',
                 'Target',
                 'Team',
                 'Extra info',
                 'Connection cohesion',
                 'Difference',
                 'Practical relevance',
                 'Budget',
                 'Requested funding',
                 'Major expenses',
                 'Other sources of income',
                 'Secured',
                 'Reach out',
                 'Heard from',
                 'Heard from other'])

    for proposal in proposals:

        result = []
        append_field = partial(_append_field, result)

        append_field(_get_proposal_url(proposal, registry))
        append_field(_get_creation_date(proposal))
        append_field(get_sheet_field(proposal, ITitle, 'title'))
        user_name, user_email = _get_user_fields(proposal)
        append_field(user_name)
        append_field(user_email)
        append_field(get_sheet_field(proposal, IUserInfo, 'first_name'))
        append_field(get_sheet_field(proposal, IUserInfo, 'last_name'))
        append_field(get_sheet_field(proposal, IOrganizationInfo, 'name'))
        append_field(get_sheet_field(proposal, IOrganizationInfo, 'city'))
        append_field(get_sheet_field(proposal, IOrganizationInfo, 'country'))
        append_field(get_sheet_field(proposal,
                                     IOrganizationInfo, 'help_request'))
        append_field(_get_date(proposal,
                               IOrganizationInfo, 'registration_date'))
        append_field(get_sheet_field(proposal, IOrganizationInfo, 'website'))
        append_field(get_sheet_field(proposal, IOrganizationInfo, 'status'))
        append_field(get_sheet_field(proposal,
                                     IOrganizationInfo, 'status_other'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPitch, 'pitch', 'pitch'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner1_name'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner1_website'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner1_country'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner2_name'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner2_website'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner2_country'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner3_name'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner3_website'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'partner3_country'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPartners, 'partners', 'other_partners'))
        append_field(' '.join(get_sheet_field(proposal, ITopic, 'topic')))
        append_field(get_sheet_field(proposal, ITopic, 'topic_other'))
        append_field(str(_get_sheet_field_from_subresource(
            proposal, IDuration, 'duration', 'duration')))
        append_field(get_sheet_field(proposal, ILocation, 'location'))
        append_field(str(get_sheet_field(proposal, ILocation, 'is_online')))
        append_field(get_sheet_field(proposal, ILocation, 'link_to_ruhr'))
        append_field(get_sheet_field(proposal, IStatus, 'status'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IChallenge, 'challenge', 'challenge'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IGoal, 'goal', 'goal'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPlan, 'plan', 'plan'))
        append_field(_get_sheet_field_from_subresource(
            proposal, ITarget, 'target', 'target'))
        append_field(_get_sheet_field_from_subresource(
            proposal, ITeam, 'team', 'team'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IExtraInfo, 'extrainfo', 'extrainfo'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IConnectionCohesion,
            'connectioncohesion', 'connection_cohesion'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IDifference, 'difference', 'difference'))
        append_field(_get_sheet_field_from_subresource(
            proposal, IPracticalRelevance,
            'practicalrelevance', 'practicalrelevance'))
        append_field(str(get_sheet_field(
            proposal, IFinancialPlanning, 'budget')))
        append_field(str(get_sheet_field(
            proposal, IFinancialPlanning, 'requested_funding')))
        append_field(get_sheet_field(proposal,
                                     IFinancialPlanning, 'major_expenses'))
        append_field(get_sheet_field(proposal, IExtraFunding, 'other_sources'))
        append_field(str(get_sheet_field(proposal, IExtraFunding, 'secured')))
        append_field(get_sheet_field(proposal,
                                     ICommunity, 'expected_feedback'))
        append_field(' '.join(get_sheet_field(proposal,
                                              ICommunity, 'heard_froms')))
        append_field(' '.join(get_sheet_field(proposal,
                                              ICommunity, 'heard_from_other')))

        wr.writerow(result)

    env['closer']()
    print('Exported mercator proposals to %s' % filename)


def _get_user_fields(proposal):
    creator = get_sheet_field(proposal, IMetadata, 'creator')
    name = get_sheet_field(creator, IUserBasic, 'name')
    email = get_sheet_field(creator, IUserExtended, 'email')
    return name, email


def _get_sheet_field_from_subresource(proposal,
                                      sheet,
                                      sheet_field,
                                      sub_sheet_field):
    sub_resource = get_sheet_field(proposal,
                                   IMercatorSubResources,
                                   sheet_field)
    return get_sheet_field(sub_resource, sheet, sub_sheet_field)


def _append_field(result, content):
    result.append(normalize_text(content))


def _get_date(resource, sheet, field):
    value = get_sheet_field(resource, sheet, field)
    if not value:
        return ''
    date = value.date().strftime('%d.%m.%Y')
    return date


def _get_creation_date(proposal):
    creation_date = get_sheet_field(
        proposal,
        IMetadata,
        'item_creation_date')
    date = creation_date.date().strftime('%d.%m.%Y')
    return date


def _get_proposal_url(proposal: IMercatorProposal,
                      registry: Registry) -> str:
    path = resource_path(proposal)
    frontend_url = registry.settings.get('adhocracy.frontend_url')
    return frontend_url + '/r' + path
