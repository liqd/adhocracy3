# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Badges
------

Badges are resources that can be badged to mark special process content.

Prerequisites
~~~~~~~~~~~~~

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.document import IDocument
    >>> from adhocracy_core.resources.document import IDocumentVersion

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

    >>> prop = {'content_type': 'adhocracy_core.resources.document.IDocument',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'proposal'}}}
    >>> resp = participant.post('/organisation/process', prop).json
    >>> proposal_version = resp['first_version_path']

Create Badge
~~~~~~~~~~~~

BadgeData can be created in `badges` pools. The IHasBadgesPool sheet of the process
gives us the right pool:


    >>> resp = initiator.get('/organisation/process').json
    >>> badges_pool = resp['data']['adhocracy_core.sheets.badge.IHasBadgesPool']['badges_pool']

# TODO First we create a badge Group pool

Now we can create BadgeData::

    >>> prop = {'content_type': 'adhocracy_core.resources.badge.IBadge',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'badge1'},
    ...                  'adhocracy_core.sheets.title.ITitle': {'title': 'Badge 1'},
    ...                  'adhocracy_core.sheets.description.IDescription': {'description': 'This is 1'},
    ...                  },
    ...         }
    >>> resp = initiator.post(badges_pool, prop).json
    >>> badge_data = resp['path']


Assign badges to process content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To assign badges we have to post a badge assignment between user, content
and badgedata to the badgeable post pool::


    >>> resp = initiator.get(proposal_version).json
    >>> post_pool = resp['data']['adhocracy_core.sheets.badge.IBadgeable']['post_pool']

    >>> user = initiator.header['X-User-Path']

    >>> prop = {'content_type': 'adhocracy_core.resources.badge.IBadgeAssignment',
    ...         'data': {'adhocracy_core.sheets.badge.IBadgeAssignment':
    ...                      {'subject': user,
    ...                       'badge': badge_data,
    ...                       'object': proposal_version}
    ...          }}
    >>> resp = initiator.post(post_pool, prop).json

Now the badged content shows the back reference targeting the badge assignment::

    >>> resp = participant.get(proposal_version).json
    >>> resp['data']['adhocracy_core.sheets.badge.IBadgeable']['assignments']
    [...organisation/process/proposal/badge_assignments/0000000/']

TODO Notes:

possible to configure what group,
                      what user,
                      exclusive?

Maybe with this data structure:

IBadgeable:{
    'assignables': [{
        'name': status,
        'select_pool': ...
        'post_pool':
        'exclusive': True,
         }
        ]
}

