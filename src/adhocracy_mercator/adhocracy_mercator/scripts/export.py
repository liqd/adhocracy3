"""Export scripts for adhocracy_mercator.

This is registered as console script in setup.py and can be used as::

    bin/export_mercator_proposals
"""

import csv
import inspect
import optparse
import os
import sys
import textwrap
import time

from pyramid.paster import bootstrap
from substanced.util import find_catalog

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

    if not os.path.exists('./var/export/'):
        os.makedirs('./var/export/')

    timestr = time.strftime('%Y%m%d-%H%M%S')

    filename = './var/export/MercatorProposalExport-%s.csv' % timestr
    result_file = open(filename, 'w', newline='')
    wr = csv.writer(result_file, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
    wr.writerow(['Einreichungsdatum',
                 'Titel',
                 'Username',
                 'First name',
                 'Last name',
                 'E-Mail des Proposers',
                 'Country User',
                 'Status Organisation',
                 'Name of Organisation',
                 'Country Organisation',
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

        # Title
        title = get_sheet_field(proposal, ITitle, 'title')
        result.append(title)

        # Username
        creator = get_sheet_field(proposal, IMetadata, 'creator')
        name = creator.name
        result.append(name)

        # First name
        first_name = get_sheet_field(proposal, IUserInfo, 'personal_name')
        result.append(first_name)

        # Last name
        last_name = get_sheet_field(proposal, IUserInfo, 'family_name')
        result.append(last_name)

        # email
        creator = get_sheet_field(proposal, IMetadata, 'creator')
        email = creator.email
        result.append(email)

        # Country
        country = get_sheet_field(proposal, IUserInfo, 'country')
        result.append(country)

        # Organisation
        organization_info = get_sheet_field(proposal,
                                            IMercatorSubResources,
                                            'organization_info')

        # status
        status = get_sheet_field(organization_info, IOrganizationInfo,
                                 'status')
        result.append(status)

        # name
        organization_name = get_sheet_field(organization_info,
                                            IOrganizationInfo,
                                            'name')
        result.append(organization_name)

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

        # Description
        description = get_sheet_field(proposal,
                                      IMercatorSubResources,
                                      'description')
        description_text = get_sheet_field(description,
                                           IDescription,
                                           'description')
        result.append(description_text)

        # Story
        story = get_sheet_field(proposal,
                                IMercatorSubResources,
                                'story')
        story_text = get_sheet_field(story,
                                     IStory,
                                     'story')
        result.append(story_text)

        # Outcome
        outcome = get_sheet_field(proposal,
                                  IMercatorSubResources,
                                  'outcome')
        outcome_text = get_sheet_field(outcome,
                                       IOutcome,
                                       'outcome')
        result.append(outcome_text)

        # Value
        value = get_sheet_field(proposal,
                                IMercatorSubResources,
                                'value')
        value_text = get_sheet_field(value,
                                     IValue,
                                     'value')
        result.append(value_text)

        # Partners
        partners = get_sheet_field(proposal,
                                   IMercatorSubResources,
                                   'partners')
        partners_text = get_sheet_field(partners,
                                        IPartners,
                                        'partners')
        result.append(partners_text)

        # Experience
        experience = get_sheet_field(proposal,
                                     IMercatorSubResources,
                                     'experience')
        experience_text = get_sheet_field(experience,
                                          IExperience,
                                          'experience')
        result.append(experience_text)

        wr.writerow(result)

    env['closer']()
    print('Exported mercator proposals to %s' % filename)
