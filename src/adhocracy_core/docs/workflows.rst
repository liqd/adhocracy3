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
    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'proposal_item'}}
    >>> resp = app_god.post_resource('/process', IDocument, data)


Workflows
---------

Workflows are finite state machines assigned to a resource.
States can set the local permissions.
States can have metadata (title, date,...).
State transitions can have a callable to execute arbitrary tasks.

The MetaAPI gives us the states and transitions metadata for each workflow::

    >>> resp = app_god.get('http://localhost/meta_api').json
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

The order these states should be listet is also set, in addition this
defines the initial workflow state (the first in the list)::

    >>> workflow['states_order']
    ['participate', 'frozen']

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

Resources have a WorkflowAssignment sheet to assign the wanted workflow::

    >>> resp = app_god.get('/process').json
    >>> workflow_data = resp['data']['adhocracy_core.sheets.workflow.ISample']
    >>> workflow_data['workflow']
    'sample'

and get the current state::

    >>> workflow_data['workflow_state']
    'participate'


in addition we have custom metadata for specific workflow states::

    >>> workflow_data['participate']['start_date']
    '2015-02-14...
    >>> workflow_data['participate']['description']
    'Start...

this metadata can be set::

    >>> data = {'data': {'adhocracy_core.sheets.workflow.ISample': {'participate': {'description': 'new',
    ...                                                                             'start_date': '2015-05-26T12:40:49.638293+00:00'}}}}
    >>> resp = app_god.put('/process/proposal_item', data)
    >>> resp.status_code
    200

    >>> resp = app_god.get('/process/proposal_item').json
    >>> workflow_data = resp['data']['adhocracy_core.sheets.workflow.ISample']
    >>> workflow_data['participate']['description']
    'new'


Workflow transition to states
-----------------------------

We can also modify the state if the workflow has a suitable transition.
First we check the available next states::

    >>> resp = app_god.options('/process/proposal_item').json
    >>> resp['PUT']['request_body']['data']['adhocracy_core.sheets.workflow.ISample']
    {'workflow_state': ['frozen']}

Then we can put the wanted next state:

     >>> data = {'data': {'adhocracy_core.sheets.workflow.ISample': {'workflow_state': 'frozen'}}}
     >>> resp = app_god.put('/process/proposal_item', data)
     >>> resp.status_code
     200

    >>> resp = app_god.get('/process/proposal_item').json
    >>> resp['data']['adhocracy_core.sheets.workflow.ISample']['workflow_state']
    'frozen'

NOTE: The available next states depend on the workflow transitions and user permissions.
NOTE: To make this work every state may have only one transition to another state.


