"""Standard workflow."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from pyrsistent import freeze

standard_meta = freeze({
    'initial_state': 'draft',
    'states': {
        'draft': {'title': 'Draft',
                  'description': 'This phase is for internal review.',
                  'acm': {'principals':                         ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                          'permissions':
                          [['view',                              'Deny',      'Deny',        'Allow',     'Allow',   'Allow',     'Allow'],
                           ['create_document',                    None,        None,         'Allow',      None,      None,        None],
                           ['edit_document',                      None,        None,         'Allow',     'Allow',   'Allow',      None],
                          ]},
                  'display_only_to_roles': ['admin', 'initiator', 'moderator'],
                  },
        'announce': {'title': 'Announce',
                     'description': '',
                     'acm': {'principals':                      ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                             'permissions':
                             [['view',                            None,        None,          None,        None,      None,        None],
                             ]},
        },
        'participate': {'title': 'Participate',
                        'description': '',
                        'acm': {'principals':                    ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                                'permissions':
                                  [['view',                       None,       'Allow',       'Allow',     'Allow',   'Allow',      None],
                                   ['create_proposal',            None,       'Allow',        None,        None,      None,        None],
                                   ['edit_proposal',              None,        None,          None,       'Allow',    None,        None],
                                   ['create_comment',             None,       'Allow',       'Allow',      None,      None,        None],
                                   ['edit_comment',               None,        None,          None,       'Allow',    None,        None],
                                   ['create_rate',                None,       'Allow',        None,        None,      None,        None],
                                   ['edit_rate',                  None,        None,          None,       'Allow',    None,        None],
                                   ['create_relation',            None,       'Allow',        None,        None,      None,        None],
                                   ['edit_relation',              None,        None,          None,       'Allow',    None,        None]
                                  ]},
                        },
        'evaluate': {'title': 'Evaluate',
                     'description': '',
                     'acm': {'principals':                      ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                             'permissions':
                             [['view',                            None,        None,          None,        None,      None,        None],
                              ['create_proposal',                 None,        None,          None,        None,      None,        None],
                              ['edit_proposal',                   None,        None,          None,        None,      None,        None],
                              ['create_comment',                  None,       'Allow',       'Allow',      None,      None,        None],
                              ['edit_comment',                    None,        None,          None,       'Allow',    None,        None],
                             ]}
        },
        'result': {'title': 'Result',
                   'description': '',
                   'acm': {'principals':                        ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                             'permissions':
                             [['view',                            None,        None,          None,        None,      None,        None],
                              ['create_proposal',                 None,        None,          None,        None,      None,        None],
                              ['edit_proposal',                   None,        None,          None,        None,      None,        None],
                              ['create_comment',                  None,        None,         'Allow',      None,     'Allow',      None],
                              ['edit_comment',                    None,        None,          None,       'Allow',    None,        None],
                             ]}
                   },
        'closed': {'title': 'Closed',
                   'description': '',
                   'acm': {'principals':                        ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                             'permissions':
                             [['view',                            None,        None,          None,        None,      None,        None],
                             ]}
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
        'to_evaluate': {'from_state': 'participate',
                        'to_state': 'evaluate',
                      },
        'to_result': {'from_state': 'evaluate',
                      'to_state': 'result',
                      },
        'to_closed': {'from_state': 'result',
                      'to_state': 'closed',
                      },
    },
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, standard_meta, 'standard')
