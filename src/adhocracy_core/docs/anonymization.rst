# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Anonymization
=============

The client may mark post/put request with the `X-Anonymize` header.
This means the current user is used for authentication/authorization,
but not visible as creator in the database or log files. Instead the
global anonymous user is used.
The Mapping between Anonymous and the real user is stored in the Database
to allow editing and personalized rating. It can be revealed by sysadmins
(direct database access is needed).


Prerequisites
~~~~~~~~~~~~~

Some imports to work with rest api calls::

    >>> from pprint import pprint

Start adhocracy app and log in some users::

    >>> log = getfixture('log')
    >>> participant = getfixture('app_participant')
    >>> anonymization_userid = getfixture('global_anonymization_userid')
    >>> admin = getfixture('app_admin')

Create participation process structure/content to get started::

    >>> prop = {'content_type': 'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'organisation'}}}
    >>> resp = admin.post('/', prop).json
    >>> prop = {'content_type': 'adhocracy_core.resources.process.IProcess',
    ...         'data': {'adhocracy_core.sheets.name.IName': {'name': 'process'}}}
    >>> resp = admin.post('/organisation', prop)


Create anonymous process content:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First we have to check if we may set the anonymize header:

    >>> resp = participant.options('/organisation/process').json
    >>> resp['POST']['request_headers']
    {'X-Anonymize': []}

Then we make a normal post request with the additional header::

    >>> prop = {'content_type': 'adhocracy_core.resources.document.IDocument',
    ...         'data': {}}
    >>> resp = participant.post('/organisation/process', prop, extra_headers={'X-Anonymize': ''}).json
    >>> proposal_path = resp['path']
    >>> proposal_version_path = resp['first_version_path']


The creator is set to anonymous::

    >>> resp = participant.get(proposal_version_path)
    >>> anonymization_userid in resp.json['data']['adhocracy_core.sheets.metadata.IMetadata']['creator']
    True

This is only True if the context we are adding to has the 'IAllowAddAnonymized'
marker sheet and the user has the 'manage_anonymized' permission.
The organisation for example is missing the right marker sheet::

    >>> resp = admin.options('/organisation').json
    >>> resp['POST']['request_headers']
    {}

If we try to set the anonymize header an error is raised

    >>> resp = admin.post('/organisation/', prop, extra_headers={'X-Anonymize': ''}).json
    >>> resp['errors']
    [...'Anonymize header not allowed'...


Edit anonymous process content:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lets check if the real creator may set the anonymize header to create
new versions:

    >>> resp = participant.options(proposal_path).json
    >>> resp['POST']['request_headers']
    {'X-Anonymize': []}


Delete anonymous process content:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lets check if the real creator may set the anonymize header to delete:

    >>> resp = participant.options(proposal_path).json
    >>> resp['DELETE']['request_headers']
    {'X-Anonymize': []}


View anonymous process content:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For non modifing requests like `get` or `options` the anonymize header
does not make sense, if set it`s just ignored.

    >>> resp = participant.get('/organisation', extra_headers={'X-Anonymize': ''})
    >>> resp.status_code
    200
