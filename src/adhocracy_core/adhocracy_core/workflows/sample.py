"""Example workflow."""

# flake8: noqa

from pyrsistent import freeze

from adhocracy_core.workflows import add_workflow

sample_meta = freeze({
    'initial_state': 'participate',
    'states': {
        'participate': {'title': 'Participate',
                  'description': 'This phase is to participate.',
                  'acm': {'principals':           ['participant', 'moderator', 'creator', 'initiator'],
                          'permissions':
                              [['create_proposal', 'Allow',        None,        None,      None],
                               ['edit_proposal',    None,          None,       'Allow',    None],
                               ['create_document', 'Allow',        None,        None,      None],
                               ['edit_document',    None,          None,       'Allow',    None],
                               ['create_comment',  'Allow',       'Allow',      None,      None],
                               ['edit_comment',     None,          None,       'Allow',    None],
                               ['create_rate',     'Allow',        None,        None,      None],
                               ['edit_rate',        None,          None,       'Allow',    None],
                               ['create_relation', 'Allow',        None,        None,      None],
                               ['edit_relation',    None,          None,       'Allow',    None]
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
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, sample_meta, 'sample')
