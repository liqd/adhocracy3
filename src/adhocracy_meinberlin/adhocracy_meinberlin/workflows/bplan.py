"""Bplan workflow."""
from pyrsistent import freeze

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta


bplan_meta = standard_meta \
             .transform(('states', 'participate', 'acm'),
                        {'principals':                    ['anonymous', 'moderator', 'creator', 'initiator'],  # noqa
                         'permissions':
                         [['create',                       'Allow',     'Allow',   'Allow',     'Allow'],  # noqa
                          ['create_proposal',              'Allow',      None,      None,        None],  # noqa
                          ['edit_proposal',                 None,        None,      None,        None],  # noqa
                         ]}) \
             .transform(('states', 'evaluate', 'acm'),
                        {'principals':                  ['anonymous', 'moderator', 'creator', 'initiator'],  # noqa
                         'permissions':
                         [['create',                      None,       'Allow',     'Allow',   'Allow'],  # noqa
                          ['create_proposal',             None,        None,        None,      None],  # noqa
                          ['edit_proposal',               None,        None,        None,      None],  # noqa
                         ]})


bplan_private_meta = freeze({
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
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, bplan_meta, 'bplan')
    add_workflow(config.registry, bplan_private_meta, 'bplan_private')
