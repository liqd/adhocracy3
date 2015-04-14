"""Export proposal.

This is registered as console script 'export_mercator_proposals'
in setup.py.
"""

import csv
import inspect
import optparse
import sys
import textwrap

from pyramid.paster import bootstrap
from substanced.util import find_catalog
from adhocracy_core.utils import create_filename

from adhocracy_core.catalog.adhocracy import index_rates
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.rate import ILikeable
from adhocracy_core.utils import get_sheet_field

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

    root = (env['root'])
    catalog = find_catalog(root, 'system')
    adhocracy_catalog = find_catalog(root, 'adhocracy')
    path = catalog['path']
    interfaces = catalog['interfaces']
    tag = adhocracy_catalog['tag']

    query = path.eq('/mercator') \
        & interfaces.eq(IMercatorProposalVersion) \
        & tag.eq('LAST')

    proposals = query.execute()

    filename = create_filename(directory='./var/export',
                               prefix='MercatorProposalExport',
                               suffix='.csv')
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
    wr.writerow(['Creation date',
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
                 'Budget',
                 'Requested Funding',
                 'Other Funding',
                 'Granted?',
                 'Ruhr-Connection',
                 'Proposal Pitch',
                 'Description',
                 'Story',
                 'Outcome',
                 'Value',
                 'Partners',
                 'Experience'])

    for proposal in proposals:

        result = []

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

        # country (somehow this always returns a country even if none has been
        # set)
        if status == 'other':
            result.append('')
        else:
            organization_country = get_sheet_field(organization_info,
                                                   IOrganizationInfo,
                                                   'country')
            result.append(organization_country)

        # Rates
        rates = get_sheet_field(proposal, ILikeable, 'post_pool')
        rates = index_rates(proposal, None)
        result.append(rates)

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

        # Ruhr-Connection
        location = get_sheet_field(proposal,
                                   IMercatorSubResources,
                                   'location')
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
        result.append(get_text_from_sheet(proposal, 'story', IStory))
        result.append(get_text_from_sheet(proposal, 'outcome', IOutcome))
        result.append(get_text_from_sheet(proposal, 'value', IValue))
        result.append(get_text_from_sheet(proposal, 'partners', IPartners))
        result.append(get_text_from_sheet(proposal, 'experience', IExperience))

        wr.writerow(result)

    env['closer']()
    print('Exported mercator proposals to %s' % filename)
