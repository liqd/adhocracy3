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
                        'acm': {'principals': [                   'anonymous', 'moderator', 'creator', 'initiator'],  # noqa
                                'permissions':
                                  [['create',                     'Allow',     'Allow',   'Allow',     'Allow'],  # noqa
                                   ['create_proposal',            'Allow',      None,      None,        None],  # noqa
                                   ['edit_proposal',               None,        None,      None,        None],  # noqa
                                   ]},
                        },
        # FIXME disable view proposals
        'frozen': {'title': 'Frozen',
                   'description': '',
                   'acm': {'principals': [                    'anonymous', 'moderator', 'creator', 'initiator'],  # noqa
                           'permissions':
                              [['create',                      None,       'Allow',     'Allow',   'Allow'],  # noqa
                               ['create_proposal',             None,        None,        None,      None],  # noqa
                               ['edit_proposal',               None,        None,        None,      None],  # noqa
                               ]},
                   },
        # FIXME disable view proposals
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


bplan_private_meta = {
    'states_order': ['private'],
    'states': {
        'private': {'title': 'Private',
                    'description': 'Disable view for non admins.',
                    'acm': {'principals': ['anonymous', 'participant'],  # noqa
                            'permissions':
                                [['view',  'Deny',      'Deny'],  # noqa
                                 ]},
                  },
    },
    'transitions': {},
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, bplan_meta, 'bplan')
    add_workflow(config.registry, bplan_private_meta, 'bplan_private')
