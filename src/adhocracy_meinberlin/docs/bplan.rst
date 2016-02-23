Imperia API
===========

This document specifies the API used by Imperia to manage bplan processes in
the a3 platform.

The following API calls are required:

- login
- create a bplan process
- edit a bplan process
- get the bplan workflow state
- make the bplan accessible

Process
-------

The full process of creation and management of a bplan has been defined as
follows:

1. Create a bplan process
2. Editing an unpublished bplan
3. Publishing a bplan
4. Editing a published bplan

API Calls
---------

Initialization::

    >>> from pprint import pprint
    >>> from webtest import TestApp
    >>> app_router = getfixture('app_router')
    >>> testapp = TestApp(app_router)
    >>> app_god = getfixture('app_god')
    >>> data = {'content_type':
    ...                'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {
    ...             'adhocracy_core.sheets.name.IName':
    ...                 {'name': 'bplan'}
    ...         }}
    >>> resp = app_god.post('/', data)

Login::

    To login post the username and password.
    The 'user_path' and 'user_token' from  the response are passed as HTTP
    custom header values in the following communication.

    >>> data = {'name': 'god',
    ...         'password': 'password'}
    >>> resp = testapp.post_json('/login_username', data)
    >>> resp.status_code
    200
    >>> user_path = resp.json['user_path']
    >>> user_token = resp.json['user_token']
    >>> auth_header = {'X-User-Path': user_path,
    ...                'X-User-Token': user_token}

Create a new bplan process::

    The creation of a bplan consist of two post request, containing all the
    required information.

    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_core.sheets.name.IName':
    ...                 {'name': '1-23'},
    ...             'adhocracy_core.sheets.title.ITitle':
    ...                 {'title': 'Bplan Title'},
    ...             'adhocracy_meinberlin.sheets.bplan.IProcessSettings':
    ...                 {'plan_number': '1-23',
    ...                  'participation_kind': 'öffentliche Auslegung'},
    ...             'adhocracy_meinberlin.sheets.bplan.IProcessPrivateSettings':
    ...                 {'office_worker_email': 'moderator@bplan.de'},
    ...             'adhocracy_core.sheets.description.IDescription':
    ...                 {'description': 'Full description',
    ...                  'short_description':'Teaser text'}
    ...             }}
    >>> resp = testapp.post_json('/bplan/', data, headers=auth_header)
    >>> resp.status_code
    200
    >>> resp.json['path']
    'http://localhost/bplan/1-23/'
    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_core.sheets.workflow.IWorkflowAssignment':
    ...                 {'state_data':
    ...                  [{'name': 'participate', 'description': 'test',
    ...                  'start_date': '2016-03-01T12:00:09',
    ...                  'end_date': '2016-05-01T12t:00:09'}]}
    ...         }}
    >>> resp = testapp.put_json('/bplan/1-23/', data, headers=auth_header)
    >>> resp.status_code
    200

Get workflow state:

    >>> resp = testapp.get('/bplan/1-23', headers=auth_header)
    >>> resp.status_code
    200
    >>> resp.json['data'] \
    ...     ['adhocracy_core.sheets.workflow.IWorkflowAssignment'] \
    ...     ['workflow_state']
    'draft'


Edit a bplan process::

    To edit a bplan the

    E.g. Changing the participation start data:

    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_core.sheets.workflow.IWorkflowAssignment':
    ...                 {'state_data':
    ...                  [{'name': 'participate', 'description': 'test',
    ...                  'start_date': '2016-03-03T12:00:09',
    ...                  'end_date': '2016-05-01T12t:00:09'}]}}}
    >>> resp = testapp.put_json('/bplan/1-23', data, headers=auth_header)
    >>> resp.status_code
    200
