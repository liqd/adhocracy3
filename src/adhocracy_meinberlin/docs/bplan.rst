Imperia API
===========

TODO:
- Describe workflow states and state transitions


Preliminaries
-------------

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.organisation import IOrganisation
    >>> from adhocracy_meinberlin.resources.bplan import IProcess
    >>> from adhocracy_core.resources.document import IDocument

Initialization::

    >>> app_god = getfixture('app_god')
    >>> app_god.base_path = '/'
    >>> data = {'content_type': 'adhocracy_core.resources.organisation.IOrganisation',
    ...         'data': {
    ...             'adhocracy_core.sheets.name.IName':
    ...                 {'name': 'bplan'}
    ...         }}
    >>> resp = app_god.post('/', data)

TODO login::

Create a new bplan process::

    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_core.sheets.name.IName':
    ...                 {'name': 'bplan123'},
    ...             'adhocracy_core.sheets.title.ITitle':
    ...                 {'title': 'Bplan Title'},
    ...             'adhocracy_meinberlin.sheets.bplan.IProcessSettings':
    ...                 { 'plan_number': '123',
    ...                   'participation_kind': 'öffentliche Auslegung',
    ...                   'participation_start_date': '2015-10-22T00:00:00+00:00',
    ...                   'participation_end_date': '2015-10-22T00:00:00+00:00'}}}
    >>> resp = app_god.post('/bplan/', data)
    >>> resp.status_code
    200
    >>> resp.json['path']
    'http://localhost/bplan/bplan123/'

Get workflow state:

    >>> resp = app_god.get('bplan/bplan123')
    >>> resp.status_code
    200
    >>> resp.json['data']['adhocracy_core.sheets.workflow.IWorkflowAssignment']['workflow_state']
    'draft'


Edit a bplan process::

    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_meinberlin.sheets.bplan.IProcessSettings':
    ...                 { 'plan_number': '123',
    ...                   'participation_kind': 'öffentliche Auslegung',
    ...                   'participation_start_date': '2015-10-22T00:00:00+00:00',
    ...                   'participation_end_date': '2015-10-22T00:00:00+00:00'}}}
    >>> resp = app_god.put('/bplan/bplan123', data)
    >>> resp.status_code
    200

Activate bplan process::

    >>> data = {'content_type': 'adhocracy_meinberlin.resources.bplan.IProcess',
    ...         'data': {
    ...             'adhocracy_core.sheets.workflow.IWorkflowAssignment':  {
    ...                 'workflow_state': 'announce'
    ...                  #'state_data':
    ...                  #    [{'name': 'announce', 'description': 'test', 'start_date': '2015-05-26T12:40:49.638293+00:00'}]
    ...         }}}
    >>> resp = app_god.put('/bplan/bplan123/', data)
    >>> resp.status_code
    200
    >>> resp = app_god.get('bplan/bplan123')
    >>> resp.status_code
    200
