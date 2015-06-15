"""Digital leben workflow."""
from adhocracy_core.workflows import add_workflow

digital_leben_meta = {
    'states_order': ['draft', 'participate', 'frozen', 'result'],
    'states': {
        'draft': {'title': 'Draft',
                  'description': 'This phase is for internal review.',
                  'acm': {'principals': [            'anonymous', 'participant', 'moderator', 'creator', 'initiator'],  # noqa
                          'permissions':
                              [['view',              'Deny',      'Deny',        'Allow',     'Allow',    'Allow'    ],  # noqa
                               ['create_proposal',    None,        None,          None,        None,      'Allow'    ],  # noqa
                               ['edit_proposal',      None,        None,          None,       'Allow',    'Allow'    ],  # noqa
                               ]},
                  'display_only_to_roles': ['admin', 'initiator', 'moderator'],
                  },
        'participate': {'title': 'Participate',
                        'description': '',
                        'acm': {'principals': [                   'participant', 'moderator', 'creator', 'initiator'],  # noqa
                                'permissions':
                                  [['create_proposal',             None,          None,        None,     'Allow'],  # noqa
                                   ['edit_proposal',               None,          None,       'Allow',   'Allow'],  # noqa
                                   ['create_comment',             'Allow',       'Allow',      None,     'Allow'],  # noqa
                                   ['edit_comment',                None,          None,       'Allow',    None  ],  # noqa
                                   ['create_rate',                'Allow',        None,        None,      None  ],  # noqa
                                   ['edit_rate',                   None,          None,       'Allow',    None  ],  # noqa
                                   ]},
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
                        'to_state': 'participate',
                        },
        'to_participate': {'from_state': 'draft',
                           'to_state': 'participate',
                           },
        'to_frozen': {'from_state': 'participate',
                      'to_state': 'frozen',
                      },
        'to_result': {'from_state': 'frozen',
                      'to_state': 'result',
                      },
    },
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, digital_leben_meta, 'digital_leben')
