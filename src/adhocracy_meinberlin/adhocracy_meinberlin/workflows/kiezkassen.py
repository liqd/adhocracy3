"""Example workflow."""
from adhocracy_core.workflows import add_workflow

kiezkassen_meta = {
    'states_order': ['draft', 'announce', 'participate', 'frozen', 'result'],
    'states': {
        'draft': {'title': 'Draft',
                  'description': 'This phase is for internal review.',
                  },
        'announce': {'title': 'Announce',
                     'description': '',
                     },
        'participate': {'title': 'Participate',
                        'description': '',
                        },
        'frozen': {'title': 'Frozen',
                   'description': '',
                   },
        'result': {'title': 'Result',
                   'description': '',
                   },
    },
    'transitions': {
        'to_announce': {'from_state': 'draft',
                        'to_state': 'announce',
                        'callback': None,
                        'permission': 'do_transitions',
                        },
        'to_participate': {'from_state': 'announce',
                           'to_state': 'participate',
                           'callback': None,
                           'permission': 'do_transitions',
                           },
        'to_participate': {'from_state': 'announce',
                           'to_state': 'participate',
                           'callback': None,
                           'permission': 'do_transitions',
                           },
        'to_frozen': {'from_state': 'participate',
                      'to_state': 'frozen',
                      'callback': None,
                      'permission': 'do_transitions',
                      },
        'to_result': {'from_state': 'frozen',
                      'to_state': 'result',
                      'callback': None,
                      'permission': 'do_transitions',
                      },
    },
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, kiezkassen_meta, 'kiezkassen')
