"""Bplan workflow."""
from adhocracy_core.workflows import add_workflow

bplan_meta = {
    'states_order': ['draft', 'announce', 'participate', 'frozen', 'result'],
    'states': {
        'draft': {'title': 'Draft',
                  'description': 'This phase is for internal review.',
                  'acm': {'principals': ['anonymous', 'participant'],  # noqa
                          'permissions':
                              [['view',  'Deny',      'Deny'],  # noqa
                               ]},
                  'display_only_to_roles': ['admin', 'initiator', 'moderator'],
                  },
        'announce': {'title': 'Announce',
                     'description': '',
                     },
        'participate': {'title': 'Participate',
                        'description': '',
                        'acm': {'principals': [                   'participant', 'moderator', 'creator', 'initiator'],  # noqa
                                'permissions':
                                  [['create_proposal',            'Allow',        None,        None,      None],  # noqa
                                   ['edit_proposal',               None,          None,        None,      None],  # noqa
                                   ]},
                        },
        'frozen': {'title': 'Frozen',
                   'description': '',
                   'acm': {'principals': [                    'participant', 'moderator', 'creator', 'initiator'],  # noqa
                           'permissions':
                              [['create_proposal',             None,          None,        None,      None],  # noqa
                               ['edit_proposal',               None,          None,        None,      None],  # noqa
                               ]},
                   },
    },
    'transitions': {
        'to_announce': {'from_state': 'draft',
                        'to_state': 'announce',
                        },
        'to_participate': {'from_state': 'announce',
                           'to_state': 'participate',
                           },
        'to_participate': {'from_state': 'announce',
                           'to_state': 'participate',
                           },
        'to_frozen': {'from_state': 'participate',
                      'to_state': 'frozen',
                      },
    },
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, bplan_meta, 'bplan')
