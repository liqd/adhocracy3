"""Export all proposals from database and write them to csv file. """
import csv
import time
import os

from pyramid.paster import bootstrap
from pyramid.threadlocal import get_current_registry

from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import ITitle
from adhocracy_mercator.sheets.mercator import IMercatorSubResources
from adhocracy_mercator.sheets.mercator import IUserInfo
from adhocracy_mercator.sheets.mercator import IFinance
from adhocracy_mercator.sheets.mercator import IOrganizationInfo

from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.rate import ILikeable
from adhocracy_core.catalog.adhocracy import index_rates

from adhocracy_core.utils import get_sheet_field

from substanced.util import find_catalog

env = bootstrap('./etc/development.ini')
root = (env['root'])

registry = get_current_registry()
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
resultFile = open('./var/export/MercatorProposalExport'
                  + timestr + '.csv', 'w', newline='')
wr = csv.writer(resultFile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
wr.writerow(['Title', 'Creator', 'Country', 'Organisation',
             'Rates', 'requested funding', 'budget'])

for proposal in proposals:

    result = []

    # Title
    title = get_sheet_field(proposal, ITitle, 'title')
    result.append(title)

    # Creator
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
    status = get_sheet_field(organization_info, IOrganizationInfo, 'status')
    result.append(status)

    # Rates
    rates = get_sheet_field(proposal, ILikeable, 'post_pool')
    rates = index_rates(proposal, None)
    result.append(rates)

    # requested funding
    finance = get_sheet_field(proposal, IMercatorSubResources, 'finance')
    budget = get_sheet_field(finance, IFinance, 'budget')
    result.append(str(budget) + ' Euro')
    requested_funding = get_sheet_field(finance, IFinance, 'requested_funding')
    result.append(str(requested_funding) + ' Euro')

    wr.writerow(result)
