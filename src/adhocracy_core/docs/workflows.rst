Workflows
==========

Preliminaries
-------------

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.process import IProcess
    >>> from adhocracy_core.resources.document import IDocument

Start adhocracy app and log in some users::

    >>> app_god = getfixture('app_god')
    >>> app_god.base_path = '/'

Lets create some content::

    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'process'}}
    >>> resp = app_god.post_resource('/', IProcess, data)
    >>> data = {}
    >>> resp = app_god.post_resource('/process', IDocument, data)


Workflows
---------

Workflows are finite state machines assigned to a resource.
States can set the local permissions.
States can have metadata (title, date,...).
State transitions can have a callable to execute arbitrary tasks.

The MetaAPI gives us the states and transitions metadata for each workflow::

    >>> resp = app_god.get('/meta_api').json
    >>> workflow = resp['workflows']['sample']

State metadata contains a human readable title::

    >>> state = workflow['states']['participate']
    >>> state['title']
    'Participate'

a description::

    >>> state['description']
    'This phase is...

a local ACM (see doc:`glossary`) that is set when entering this state::

    >>> state['acm']['principals']
    ['participant', ...
    >>> state['acm']['permissions']
    [['create_proposal',...

a hint for the frontend if displaying this state in listing should be restricted::

    >>> state['display_only_to_roles']
    []

The initial workflow state::

    >>> workflow['initial_state']
    'participate'

Transition metadata determines the possible state flow and can provide a callable to
execute arbitrary tasks::

     >>> transition = workflow['transitions']['to_frozen']
     >>> pprint(transition)
     {'callback': None,
      'from_state': 'participate',
      'permission': 'do_transition',
      'to_state': 'frozen'}


Workflow Assignment
-------------------

Pool have a WorkflowAssignment sheet to get the registered workflow::

    >>> resp = app_god.get('/process/').json
    >>> workflow_data = resp['data']['adhocracy_core.sheets.workflow.IWorkflowAssignment']
    >>> workflow_data['workflow']
    'sample'

and get the current state::

    >>> workflow_data['workflow_state']
    'participate'


in addition it can have custom metadata for specific workflow states::

    >>> workflow_data['state_data']
    []

this metadata can be set::

    >>> data = {'data': {'adhocracy_core.sheets.workflow.IWorkflowAssignment':  {'state_data':
    ...                  [{'name': 'participate', 'description': 'new',
    ...                    'start_date': '2015-05-26T12:40:49.638293+00:00'}]
    ...         }}}
    >>> resp = app_god.put('/process', data)
    >>> resp.status_code
    200

    >>> resp = app_god.get('/process').json
    >>> workflow_data = resp['data']['adhocracy_core.sheets.workflow.IWorkflowAssignment']
    >>> pprint(workflow_data['state_data'][0])
    {'description': 'new',
     'name': 'participate',
     'start_date': '2015-05-26T12:40:49.638293+00:00'}



Workflow transition to states
-----------------------------

We can also modify the state if the workflow has a suitable transition.
First we check the available next states::

    >>> resp = app_god.options('/process').json
    >>> resp['PUT']['request_body']['data']['adhocracy_core.sheets.workflow.IWorkflowAssignment']
    {'workflow_state': ['frozen']}

Then we can put the wanted next state:

     >>> data = {'data': {'adhocracy_core.sheets.workflow.IWorkflowAssignment': {'workflow_state': 'frozen'}}}
     >>> resp = app_god.put('/process', data)
     >>> resp.status_code
     200

    >>> resp = app_god.get('/process').json
    >>> resp['data']['adhocracy_core.sheets.workflow.IWorkflowAssignment']['workflow_state']
    'frozen'

NOTE: The available next states depend on the workflow transitions and user permissions.
NOTE: To make this work every state may have only one transition to another state.


Workflow State filtering
------------------------

Filtering Pools allow to search for resource with specific workflow state:

    >>> resp_data = app_god.get('/', {'workflow_state': 'WRONG'}).json
    >>> pprint(resp_data['data']['adhocracy_core.sheets.pool.IPool']['elements'])
    []

    >>> resp_data = app_god.get('/', {'workflow_state': 'frozen'}).json
    >>> pprint(resp_data['data']['adhocracy_core.sheets.pool.IPool']['elements'])
    ['.../process/']

