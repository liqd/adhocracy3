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


def export_proposals():
    """
    Export all proposals from database and write them to csv file.

    --limited restricts the export to a few fields.
    """
    doc = textwrap.dedent(inspect.getdoc(export_proposals))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('config')
    parser.add_argument('-l',
                        '--limited',
                        help='only export a limited subset of all fields',
                        action='store_true')
    args = parser.parse_args()
    env = bootstrap(args.config)
    root = env['root']
    registry = env['registry']
    _export_proposals(root, registry, args.limited)
    env['closer']()


def _export_proposals(root, registry, limited):
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

    include_field = True
    exclude_field = False
    fields = \
        [('URL', include_field,
          partial(_get_proposal_url, registry)),
         ('Creation date', include_field,
          partial(_get_creation_date)),
         ('Title', include_field,
          partial(_get_sheet_field, ITitle, 'title')),
         ('Creator name', include_field,
          partial(_get_creator_name)),
         ('Creator email', include_field,
          partial(_get_creator_email)),
         ('First name', include_field,
          partial(_get_sheet_field, IUserInfo, 'first_name')),
         ('Last name', include_field,
          partial(_get_sheet_field, IUserInfo, 'last_name')),
         ('Organisation name', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'name')),
         ('Organisation city', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'city')),
         ('Organisation country', include_field,
          partial(_get_sheet_field, IOrganizationInfo, 'country')),
         ('Organisation help request', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'help_request')),
         ('Organisation registration date', exclude_field,
          partial(_get_date, IOrganizationInfo, 'registration_date')),
         ('Organisation website', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'website')),
         ('Organisation status', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'status')),
         ('Organisation status other', exclude_field,
          partial(_get_sheet_field, IOrganizationInfo, 'status_other')),
         ('Pitch', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPitch, 'pitch', 'pitch')),
         ('Partner1 name', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner1_name')),
         ('Partner1 website', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner1_website')),
         ('Partner1 country', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner1_country')),
         ('Partner2 name', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner2_name')),
         ('Partner2 website', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner2_website')),
         ('Partner2 country', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner2_country')),
         ('Partner3 name', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner3_name')),
         ('Partner3 website', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner3_website')),
         ('Partner3 country', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'partner3_country')),
         ('Others partners', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPartners, 'partners', 'other_partners')),
         ('Topics', exclude_field,
          lambda proposal: ' '.join(
              get_sheet_field(proposal, ITopic, 'topic'))),
         ('Topic other', exclude_field,
          partial(_get_sheet_field, ITopic, 'topic_other')),
         ('Duration', exclude_field,
          lambda proposal: str(_get_sheet_field_from_subresource(
              IDuration, 'duration', 'duration', proposal))),
         ('Location', exclude_field,
          partial(_get_sheet_field, ILocation, 'location')),
         ('Is online', exclude_field,
          lambda proposal: str(
              get_sheet_field(proposal, ILocation, 'is_online'))),
         ('Link to Ruhr', exclude_field,
          partial(_get_sheet_field, ILocation, 'link_to_ruhr')),
         ('Status', exclude_field,
          partial(_get_sheet_field, IStatus, 'status')),
         ('Challenge', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IChallenge, 'challenge', 'challenge')),
         ('Goal', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IGoal, 'goal', 'goal')),
         ('Plan', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPlan, 'plan', 'plan')),
         ('Target', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  ITarget, 'target', 'target')),
         ('Team', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  ITeam, 'team', 'team')),
         ('Extra info', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IExtraInfo, 'extrainfo', 'extrainfo')),
         ('Connection cohesion', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IConnectionCohesion,
                  'connectioncohesion', 'connection_cohesion')),
         ('Difference', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IDifference,
                  'difference', 'difference')),
         ('Practical relevance', exclude_field,
          partial(_get_sheet_field_from_subresource,
                  IPracticalRelevance,
                  'practicalrelevance', 'practicalrelevance')),
         ('Budget', exclude_field,
          lambda proposal: str(get_sheet_field(
              proposal, IFinancialPlanning, 'budget'))),
         ('Requested funding', exclude_field,
          lambda proposal: str(get_sheet_field(
              proposal, IFinancialPlanning, 'requested_funding'))),
         ('Major expenses', exclude_field,
          partial(_get_sheet_field,
                  IFinancialPlanning, 'major_expenses')),
         ('Other sources of income', exclude_field,
          partial(_get_sheet_field, IExtraFunding, 'other_sources')),
         ('Secured', exclude_field,
          lambda proposal: str(get_sheet_field(
              proposal, IExtraFunding, 'secured'))),
         ('Reach out', exclude_field,
          partial(_get_sheet_field, ICommunity, 'expected_feedback')),
         ('Heard from', exclude_field,
          lambda proposal: ' '.join(get_sheet_field(
              proposal, ICommunity, 'heard_froms'))),
         ('Heard from other', exclude_field,
          lambda proposal: ' '.join(get_sheet_field(
              proposal, ICommunity, 'heard_from_other')))]

    wr.writerow([name for (name, is_included, _) in fields
                 if is_included or not limited])

    for proposal in proposals:

        result = []
        append_field = partial(_append_field, result)

        for name, is_in, get_field in fields:
            if is_in or not limited:
                append_field(get_field(proposal))

        wr.writerow(result)

    print('Exported mercator proposals to %s' % filename)


def _get_user_fields(proposal):
    creator = get_sheet_field(proposal, IMetadata, 'creator')
    name = get_sheet_field(creator, IUserBasic, 'name')
    email = get_sheet_field(creator, IUserExtended, 'email')
    return name, email


def _get_sheet_field_from_subresource(sheet,
                                      sheet_field,
                                      sub_sheet_field,
                                      proposal):
    sub_resource = get_sheet_field(proposal,
                                   IMercatorSubResources,
                                   sheet_field)
    return get_sheet_field(sub_resource, sheet, sub_sheet_field)


def _normalize_text(s: str) -> str:
    """Normalize text to put it in CVS."""
    return s.replace(';', '')


def _append_field(result, content):
    result.append(_normalize_text(content))


def _get_date(sheet, field, resource):
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


def _get_proposal_url(registry: Registry,
                      proposal: IMercatorProposal) -> str:
    path = resource_path(proposal)
    frontend_url = registry.settings.get('adhocracy.frontend_url')
    return frontend_url + '/r' + path


def _get_sheet_field(sheet, field, resource):
    return get_sheet_field(resource, sheet, field)


def _get_creator_name(proposal):
    creator = get_sheet_field(proposal, IMetadata, 'creator')
    name = get_sheet_field(creator, IUserBasic, 'name')
    return name


def _get_creator_email(proposal):
    creator = get_sheet_field(proposal, IMetadata, 'creator')
    email = get_sheet_field(creator, IUserExtended, 'email')
    return email
