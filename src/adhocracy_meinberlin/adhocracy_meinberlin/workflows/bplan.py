"""Bplan workflow."""

# flake8: noqa

from pyrsistent import freeze

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta


bplan_meta = standard_meta \
             .transform(('states', 'participate', 'acm'),
                        {'principals':                    ['anonymous', 'moderator', 'creator', 'initiator'],
                         'permissions':
                         [['create',                       'Allow',     'Allow',   'Allow',     'Allow'],
                          ['create_proposal',              'Allow',      None,      None,        None],
                          ['edit_proposal',                 None,        None,      None,        None],
                         ]}) \
             .transform(('states', 'evaluate', 'acm'),
                        {'principals':                  ['anonymous', 'moderator', 'creator', 'initiator'],
                         'permissions':
                         [['create',                      None,       'Allow',     'Allow',   'Allow'],
                          ['create_proposal',             None,        None,        None,      None],
                          ['edit_proposal',               None,        None,        None,      None],
                         ]})


bplan_private_meta = freeze({
    'initial_state': 'private',
    'states': {
        'private': {'title': 'Private',
                    'description': 'Disable view for non admins.',
                    'acm': {'principals': ['anonymous', 'participant'],
                            'permissions':
                                [['view',  'Deny',      'Deny'],
                                 ]},
                  },
    },
    'transitions': {},
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, bplan_meta, 'bplan')
    add_workflow(config.registry, bplan_private_meta, 'bplan_private')
