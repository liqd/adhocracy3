"""Agenda s1 workflow."""

# flake8: noqa
from pyramid.request import Request
from pyrsistent import freeze
from adhocracy_core.interfaces import IPool
from adhocracy_core.workflows import add_workflow


def change_children_to_voteable(context: IPool, request: Request, **kwargs):
    """Do transition from state proposed to voteable for all children."""
    for child in context.values():
        workflow = request.registry.content.get_workflow(child)
        if workflow is None:
            continue
        state = workflow.state_of(child)
        if state == 'proposed':
            workflow.transition_to_state(child, request, 'voteable')


def change_children_to_rejected(context: IPool, request: Request, **kwargs):
    """Do transition from state proposed to rejected for all children."""
    for child in context.values():
        workflow = request.registry.content.get_workflow(child)
        if workflow is None:
            continue
        state = workflow.state_of(child)
        if state == 'voteable':
            workflow.transition_to_state(child, request, 'rejected')


s1_meta = freeze({
    'initial_state': 'propose',
    'states': {
        'propose': {'title': 'Participate',
                    'description': '',
                    'acm': {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                            'permissions':
                                  [['create_proposal',            'Allow',        None,        None,     'Allow'],
                                   ['edit_proposal',               None,          None,       'Allow',    None],
                                   ['create_comment',             'Allow',       'Allow',      None,     'Allow'],
                                   ['edit_comment',                None,          None,       'Allow',    None],
                                   ['create_rate',                'Allow',        None,        None,      None],
                                   ['edit_rate',                   None,          None,       'Allow',    None],
                                   ]},
                        },
        'select': {'title': 'Evaluate',
                   'description': '',
                   'acm': {'principals':                     ['participant', 'moderator', 'creator', 'initiator'],
                           'permissions':
                             [['create_proposal',            'Allow',        None,        None,     'Allow'],
                              ['edit_proposal',               None,          None,       'Allow',    None],
                              ['create_rate',                'Allow',        None,        None,      None],
                              ['edit_rate',                   None,          None,       'Allow',    None],
                              ['create_comment',             'Allow',       'Allow',      None,     'Allow'],
                              ['edit_comment',                None,          None,       'Allow',    None],
                             ]}
        },
        'result': {'title': 'Result',
                   'description': '',
                   'acm': {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                           'permissions':
                                  [['create_proposal',            'Allow',        None,        None,     'Allow'],
                                   ['edit_proposal',               None,          None,       'Allow',    None],
                                   ['create_comment',             'Allow',       'Allow',      None,     'Allow'],
                                   ['edit_comment',                None,          None,       'Allow',    None],
                                   ['create_rate',                'Allow',        None,        None,      None],
                                   ['edit_rate',                   None,          None,       'Allow',    None],
                                   ]},
                        },
    },
    'transitions': {
        'to_select': {'from_state': 'propose',
                      'to_state': 'select',
                      'callback': 'adhocracy_s1.workflows.s1.change_children_to_voteable',
                      },
        'to_result': {'from_state': 'select',
                      'to_state': 'result',
                      'callback': 'adhocracy_s1.workflows.s1.change_children_to_rejected',
                      },
        'to_propose': {'from_state': 'result',
                       'to_state': 'propose',
                      },
    },
})


s1_content_meta = freeze({
    'initial_state': 'proposed',
    'states': {
        'proposed': {},
        'voteable': {},
        'selected': {},
        'rejected': {},
    },
    'transitions': {
        'to_votable': {'from_state': 'proposed',
                       'to_state': 'voteable',
                       },
        'to_selected': {'from_state': 'voteable',
                        'to_state': 'selected',
                       },
        'to_rejected': {'from_state': 'voteable',
                        'to_state': 'rejected',
                        },
    },
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, s1_meta, 's1')
    add_workflow(config.registry, s1_content_meta, 's1_content')
