"""Script to export proposal."""

import argparse
import csv
import inspect
import textwrap

from pyramid.registry import Registry
from pyramid.paster import bootstrap
from substanced.util import find_service
from adhocracy_core.utils import create_filename

from adhocracy_core.catalog.adhocracy import index_rates
from adhocracy_core.catalog.adhocracy import index_comments
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.interfaces import search_query

from pyramid.traversal import resource_path

from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import IFinance
from adhocracy_mercator.sheets.mercator import IMercatorSubResources
from adhocracy_mercator.sheets.mercator import IOrganizationInfo
from adhocracy_mercator.sheets.mercator import IUserInfo
from adhocracy_mercator.sheets.mercator import ILocation
from adhocracy_mercator.sheets.mercator import IIntroduction
from adhocracy_mercator.sheets.mercator import IDescription
from adhocracy_mercator.sheets.mercator import IHeardFrom
from adhocracy_mercator.sheets.mercator import IStory
from adhocracy_mercator.sheets.mercator import IOutcome
from adhocracy_mercator.sheets.mercator import IValue
from adhocracy_mercator.sheets.mercator import IPartners
from adhocracy_mercator.sheets.mercator import IExperience
from adhocracy_mercator.sheets.mercator import ISteps


def normalize_text(s: str) -> str:
    """Normalize text to put it in CVS."""
    return s.replace(';', '')


def get_text_from_sheet(proposal, field, isheet, registry):
    """Get text from sheetfields and return it."""
    retrieved_field = registry.content.get_sheet_field(proposal,
                                                       IMercatorSubResources,
                                                       field)
    field_text = registry.content.get_sheet_field(retrieved_field,
                                                  isheet,
                                                  field)
    return normalize_text(field_text)


def get_heard_from_text(heardfrom: dict) -> str:
    """Return text for the 'heard from' field."""
    def kv_to_text(k, v):
        if k == 'heard_elsewhere':
            return normalize_text(v)
        return {'heard_from_colleague': 'colleague',
                'heard_from_facebook': 'facebook',
                'heard_from_newsletter': 'newsletter',
                'heard_from_website': 'website'}[k]

    return ','.join([kv_to_text(k, v) for (k, v) in heardfrom.items() if v])


def main():
    """Export all proposals from database and write them to csv file."""
    doc = textwrap.dedent(inspect.getdoc(main))
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument('config')
    args = parser.parse_args()

    env = bootstrap(args.config)

    root = env['root']
    registry = env['registry']
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=IMercatorProposalVersion,
                                  sort_by='rates',
                                  reverse=True,
                                  indexes={'tag': 'LAST'},
                                  resolve=True,
                                  )
    proposals = catalogs.search(query).elements

    filename = create_filename(directory='./var/export',
                               prefix='MercatorProposalExport',
                               suffix='.csv')
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)

    wr.writerow(['URL',
                 'Creation date',
                 'Title',
                 'Username',
                 'First name',
                 'Last name',
                 'Creator email',
                 'Creator country',
                 'Organisation status',
                 'Organisation name',
                 'Organisation country',
                 'Rates (Votes)',
                 'Number of Comments',
                 'Budget',
                 'Requested Funding',
                 'Other Funding',
                 'Granted?',
                 'Location Places',
                 'Location Online',
                 'Location Ruhr-Connection',
                 'Proposal Pitch',
                 'Description',
                 'How do you want to get there?',
                 'Story',
                 'Outcome',
                 'Value',
                 'Partners',
                 'Experience',
                 'Heard from'])

    get_sheet_field = registry.content.get_sheet_field
    for proposal in proposals:

        result = []

        result.append(_get_proposal_url(proposal, registry))

        # Creationdate
        creation_date = get_sheet_field(
            proposal,
            IMetadata,
            'item_creation_date',
        )
        date = creation_date.date().strftime('%d.%m.%Y')
        result.append(date)
        result.append(get_sheet_field(proposal, ITitle, 'title'))
        creator = get_sheet_field(proposal, IMetadata, 'creator')
        if creator is None:
            name = ''
            email = ''
        else:
            name = get_sheet_field(creator, IUserBasic, 'name')
            email = get_sheet_field(creator, IUserExtended, 'email')
        result.append(name)
        result.append(get_sheet_field(proposal, IUserInfo, 'personal_name'))
        result.append(get_sheet_field(proposal, IUserInfo, 'family_name'))
        result.append(email)
        result.append(get_sheet_field(proposal, IUserInfo, 'country'))

        # Organisation
        organization_info = get_sheet_field(proposal,
                                            IMercatorSubResources,
                                            'organization_info')

        # status
        status = get_sheet_field(organization_info, IOrganizationInfo,
                                 'status')
        result.append(status)

        # name
        result.append(get_sheet_field(organization_info,
                                      IOrganizationInfo,
                                      'name'))

        # country
        if status == 'other':
            result.append('')
        else:
            organization_country = get_sheet_field(organization_info,
                                                   IOrganizationInfo,
                                                   'country')
            result.append(organization_country)

        # Rates
        rates = index_rates(proposal, None)
        result.append(rates)

        # Comments
        comments = index_comments(proposal, None)
        result.append(comments)

        # requested funding
        finance = get_sheet_field(proposal,
                                  IMercatorSubResources,
                                  'finance')
        budget = get_sheet_field(finance, IFinance, 'budget')
        result.append(str(budget))
        requested_funding = get_sheet_field(finance, IFinance,
                                            'requested_funding')
        result.append(str(requested_funding))
        other_funding = get_sheet_field(finance, IFinance,
                                        'other_sources')
        result.append(other_funding)
        if other_funding:
            granted = get_sheet_field(finance, IFinance,
                                      'granted')
        else:
            granted = ''

        result.append(granted)

        location = get_sheet_field(proposal,
                                   IMercatorSubResources,
                                   'location')

        # Location Places

        location_is_specific = get_sheet_field(
            location,
            ILocation,
            'location_is_specific')

        locations = []

        if location_is_specific:
            location1 = locations.append(get_sheet_field(
                location,
                ILocation,
                'location_specific_1'))
            if location1:
                locations.append(location1)

            location2 = locations.append(get_sheet_field(
                location,
                ILocation,
                'location_specific_2'))
            if location2:
                locations.append(location2)

            location3 = locations.append(get_sheet_field(
                location,
                ILocation,
                'location_specific_3'))
            if location3:
                locations.append(location3)

        result.append('  '.join(locations))

        is_online = get_sheet_field(
            location,
            ILocation,
            'location_is_online')
        result.append(is_online)

        # Ruhr-Connection

        ruhr_connection = get_sheet_field(
            location,
            ILocation,
            'location_is_linked_to_ruhr')
        result.append(ruhr_connection)

        # Proposal Pitch
        introduction = get_sheet_field(
            proposal,
            IMercatorSubResources,
            'introduction')
        teaser = get_sheet_field(introduction,
                                 IIntroduction,
                                 'teaser')
        result.append(teaser)

        result.append(
            get_text_from_sheet(
                proposal,
                'description',
                IDescription,
                registry,
            ))
        result.append(get_text_from_sheet(proposal, 'steps', ISteps, registry))
        result.append(get_text_from_sheet(proposal, 'story', IStory, registry))
        result.append(get_text_from_sheet(proposal, 'outcome', IOutcome,
                                          registry))
        result.append(get_text_from_sheet(proposal, 'value', IValue, registry))
        result.append(get_text_from_sheet(proposal, 'partners', IPartners,
                                          registry))
        result.append(get_text_from_sheet(proposal, 'experience', IExperience,
                                          registry))

        # Heard from
        heard_from = registry.content.get_sheet(proposal, IHeardFrom)
        result.append(get_heard_from_text(heard_from.get()))

        wr.writerow(result)

    env['closer']()
    print('Exported mercator proposals to %s' % filename)


def _get_proposal_url(proposal: IMercatorProposalVersion,
                      registry: Registry) -> str:
    path = resource_path(proposal)
    frontend_url = registry.settings.get('adhocracy.canonical_url')
    return frontend_url + '/r' + path
