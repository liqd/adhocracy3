# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Badges
------

Badges are resources that can be baged to mark special process content.

Prerequisites
~~~~~~~~~~~~~

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.sample_proposal import IProposal
    >>> from adhocracy_core.resources.sample_proposal import IProposalVersion

Start adhocracy app and log in some users::

    >>> participant = getfixture('app_participant')
    >>> initiator = getfixture('app_initiator')
    >>> admin = getfixture('app_admin')

Create participation process structure/content to get started::

    >>> prop = {'content_type': 'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'organisation'}}}
    >>> resp = admin.post('/', prop).json
    >>> prop = {'content_type': 'adhocracy_core.resources.process.IProcess',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'process'}}}
    >>> resp = admin.post('/organisation', prop)

    >>> prop = {'content_type': 'adhocracy_core.resources.sample_proposal.IProposal',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'proposal'}}}
    >>> resp = participant.post('/organisation/process', prop).json
    >>> proposal_version = resp['first_version_path']

Create Badge
~~~~~~~~~~~~

Badges can be created in `badges` pools. The IHasBadgesPool sheet of the process
gives us the right pool:


    >>> resp = initiator.get('/organisation/process').json
    >>> badges = resp['data']['adhocracy_core.sheets.badge.IHasBadgesPool']['badges_pool']

# TODO First we crate a badge Group pool

Now we can create a Badge

    >>> prop = {'content_type': 'adhocracy_core.resources.badge.IBadge',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'badge1'},
    ...                  'adhocracy_core.sheets.badge.IBadgeData':
    ...                       {'title': 'Badge 1',
    ...                         'description': 'This badge show greatness.',
    ...                         'color': '#666666',
    ...                        },
    ...         }}
    >>> resp = initiator.post(badges, prop).json
    >>> badge = resp['path']


Badge Process Content
~~~~~~~~~~~~~~~~~~~~~

To assign badges to content we have to edit an existing badge::

    >>> prop = {'content_type': 'adhocracy_core.resources.badge.IBadge',
    ...         'data': {'adhocracy_core.sheets.badge.IBadgeAssignments':
    ...                      {'badges': [proposal_version]},
    ...          }}
    >>> resp = initiator.put(badge, prop)

Now the badged content shows the back reference targeting the badge::

    >>> resp = participant.get(proposal_version).json
    >>> resp['data']['adhocracy_core.sheets.badge.IBadgeable']['badged_by']
    [.../organisation/process/badges/badge1/']
