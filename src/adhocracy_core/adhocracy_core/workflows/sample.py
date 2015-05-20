"""Example workflow."""
from adhocracy_core.workflows import add_workflow

sample_meta = {
    'states_order': ['participate', 'frozen'],
    'states': {
        'participate': {'title': 'Participate',
                  'description': 'This phase is to participate.',
                  'acm': {'principals':           ['participant', 'moderator', 'creator', 'initiator'],  # noqa
                          'permissions':
                              [['create_proposal', 'Allow',        None,        None,      None],  # noqa
                               ['edit_proposal',    None,          None,       'Allow',    None],  # noqa
                               ['create_comment',  'Allow',       'Allow',      None,      None],  # noqa
                               ['edit_comment',     None,          None,       'Allow',    None],  # noqa
                               ['create_rate',     'Allow',        None,        None,      None],  # noqa
                               ['edit_rate',        None,          None,       'Allow',    None],  # noqa
                               ]},
                  'display_only_to_roles': [],
                  },
        'frozen': {'title': 'Frozen',
                   'description': '',
                   'acm': {},
                   'display_only_to_roles': [],
                   },
    },
    'transitions': {
        'to_frozen': {'from_state': 'participate',
                      'to_state': 'frozen',
                      'callback': None,
                      'permission': 'do_transition',
                      },
        },
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, sample_meta, 'sample')
