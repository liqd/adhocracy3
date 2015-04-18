"""Export proposal.

This is registered as console script 'export_mercator_proposals'
in setup.py.
"""

import csv
import inspect
import optparse
import sys
import textwrap

from pyramid.registry import Registry
from pyramid.paster import bootstrap
from adhocracy_core.utils import create_filename

from adhocracy_core.catalog.adhocracy import index_rates
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.utils import get_sheet

from pyramid.traversal import resource_path

from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import IFinance
from adhocracy_mercator.sheets.mercator import IMercatorSubResources
from adhocracy_mercator.sheets.mercator import IOrganizationInfo
from adhocracy_mercator.sheets.mercator import ITitle
from adhocracy_mercator.sheets.mercator import IUserInfo
from adhocracy_mercator.sheets.mercator import ILocation
from adhocracy_mercator.sheets.mercator import IIntroduction
from adhocracy_mercator.sheets.mercator import IDescription
from adhocracy_mercator.sheets.mercator import IStory
from adhocracy_mercator.sheets.mercator import IOutcome
from adhocracy_mercator.sheets.mercator import IValue
from adhocracy_mercator.sheets.mercator import IPartners
from adhocracy_mercator.sheets.mercator import IExperience
from adhocracy_mercator.sheets.mercator import ISteps


def get_text_from_sheet(proposal, field, sheet):
    """Get text from sheetfields and return it. """
    retrieved_field = get_sheet_field(proposal, IMercatorSubResources, field)
    field_text = get_sheet_field(
        retrieved_field,
        sheet,
        field).replace(
        ';',
        '')
    return field_text


def export_proposals():
    """Export all proposals from database and write them to csv file. """
    usage = 'usage: %prog config_file'
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(inspect.getdoc(export_proposals))
    )
    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 1:
        print('You must provide at least one argument')
        return 2

    env = bootstrap(args[0])

    root = env['root']
    registry = env['registry']
    pool = get_sheet(root, IPool)
    params = {'depth': 3,
              'content_type': IMercatorProposalVersion,
              'sort': 'rates',
              'reverse': True,
              'tag': 'LAST',
              'elements': 'content',
              }
    results = pool.get(params)
    proposals = results['elements']

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
                 'Experience'])

    for proposal in proposals:

        result = []

        result.append(_get_proposal_url(proposal, registry))

        # Creationdate
        creation_date = get_sheet_field(
            proposal,
            IMetadata,
            'item_creation_date')
        date = creation_date.date().strftime('%d.%m.%Y')
        result.append(date)

        result.append(get_sheet_field(proposal, ITitle, 'title'))
        result.append(get_sheet_field(proposal, IMetadata, 'creator').name)
        result.append(get_sheet_field(proposal, IUserInfo, 'personal_name'))
        result.append(get_sheet_field(proposal, IUserInfo, 'family_name'))
        result.append(get_sheet_field(proposal, IMetadata, 'creator').email)
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
        query = {'content_type': ICommentVersion,
                 'depth': 'all',
                 'tag': 'LAST',
                 'count': 'true',
                 'elements': 'omit'}
        proposal_item = proposal.__parent__
        proposal_sheet = get_sheet(proposal_item, IPool)
        query_result = proposal_sheet.get(query)
        result.append(query_result['count'])

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
                IDescription))
        result.append(get_text_from_sheet(proposal, 'steps', ISteps))
        result.append(get_text_from_sheet(proposal, 'story', IStory))
        result.append(get_text_from_sheet(proposal, 'outcome', IOutcome))
        result.append(get_text_from_sheet(proposal, 'value', IValue))
        result.append(get_text_from_sheet(proposal, 'partners', IPartners))
        result.append(get_text_from_sheet(proposal, 'experience', IExperience))

        wr.writerow(result)

    env['closer']()
    print('Exported mercator proposals to %s' % filename)


def _get_proposal_url(proposal: IMercatorProposalVersion,
                      registry: Registry) -> str:
    path = resource_path(proposal)
    frontend_url = registry.settings.get('adhocracy.frontend_url')
    return frontend_url + '/r' + path
