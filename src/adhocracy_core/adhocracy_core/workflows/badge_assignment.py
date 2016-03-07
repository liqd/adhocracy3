"""
Badge assignment workflow.

This workflow can be defined on badge resources to specify who are
allowed to assign them.

"""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from pyrsistent import freeze

badge_assignment_meta = freeze({
    'initial_state': 'assign',
    'states': {
        'assign': {'title': 'Assignment',
                  'description': 'Assign badges.',
                  'acm': {'principals':                         ['anonymous', 'participant', 'moderator', 'creator', 'initiator', 'admin'],
                          'permissions':
                          [['assign_badge',                       None,       'Allow',       'Allow',      None,      None,        None],
                          ]}
                  },
        },
    'transitions': {
    }
})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, badge_assignment_meta, 'badge_assignment')
