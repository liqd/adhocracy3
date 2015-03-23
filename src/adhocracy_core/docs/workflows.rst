Workflows
==========

Preliminaries
-------------

For testing, we need to import some stuff and start the Adhocracy testapp::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.pool import IBasicPool
    >>> from adhocracy_core.resources.sample_proposal import IProposal
    >>> app_god = getfixture('app_god')
    >>> app_god.base_path = '/adhocracy'

Lets create some content::

    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'proposals'}}
    >>> resp = app_god.post_resource('/', IBasicPool, data)
    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'proposal_item'}}
    >>> resp = app_god.post_resource('/proposals', IProposal, data)


Workflows
---------

Workflows are finite state machines assigned to a resource.
States can set the local permissions.
States can have metadata (title, date,...).
State transitions can have a callable to execute arbitrary tasks.

.. TODO:: nice Introduction.

The MetaAPI gives us the states and transitions metadata for each workflow::

    >>> resp_data = app_god.get('/../meta_api').json
    >>> worklow = resp_data['worklows']['sampleworkflow']

State metadata contains a human readable title::

    >>> state = workflow['states']['announced']
    >>> state['title']
    'Announced'

a description::

    >>> state['description']
    'In this phase you may wait.'

a local ACL (see doc:`authorization`) that is set when entering this state::

    >>> state['acl']
    [('Disallow, 'role:reader', 'view')]

a hint for the frontend if displaying this state in listing should be restricted::

    >>> state['display_only_to_roles']
    ['Manager']

The order these states should be listet is also set, in addition this
defines the initial workflow state (the first in the list)::

    >>> workflow['states_order']
    ['draft', 'announced', 'published']

Transition metadata determines the possible state flow and can provide a callable to
execute arbitrary tasks::

     >>> transition = workflow['transitions']['to_announced']
     >>> pprint(transition)
     {
      'callback': 'adhocracy_core.workflows.samplecallback',
      'from_state': 'draft',
      'to_state': 'announced',
      'permission': 'review',
      }


Workflow Assigment
------------------

Resources have a WorkflowAssigenment sheet to assign the wanted workflow::

    >>> resp_data = app_god.get('/proposals/proposal_item').json
    >>> workflow_data = resp_data['data']['adhocracy_core.sheets.workflow.ISampleWorkflowAssignment']
    >>> workflow_data['workflow_type']
    'sampleworkflow'

in addition we can add custom metadata for specific workflow states::

    >>> workflow_data['announced']['start_date']
    '2015-02-14...,
    >>> workflow_data['announced']['description]
    'Soon you can participate...


Workflow transition to states
-----------------------------

The metadata sheets shows the current workflow state::

    >>> resp_data = app_god.get('/proposals/proposal_item').json
    >>> metadata_data = resp_data['data']['adhocracy_core.sheets.metadata.IMetadataSheet']
    >>> workflow_data['workflow_state']
    'announced'

We can also modify the state if the workflow has a suitable transition::

    >>> resp_data = app_god.options('/proposals/proposal_item')
    >>> available_next_states = resp_data['PUT']['adhocracy_core.sheets.metadata.IMetadataSheet'][workflow_state]
    ['published']

NOTE: The available next states depend on the workflow transitions and user permissions.
NOTE: To make this work every state may have only one transition to another state.

TODO: How to hide resources and subresources if needed for state?
      We can set/remove the local view permission for the resource.
      Then you cannot do GET requests anymore. But we never implemented this
      properly, you can still view the resource in listings and the client
      expects that its possible to do GET requests.
