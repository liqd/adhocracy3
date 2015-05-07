"""Example workflow."""
from adhocracy_core.workflows import add_workflow

sample_meta = {
    'states_order': ['draft', 'announced'],
    'states': {
        'draft': {'title': 'Draft',
                  'description': 'This phase is for internal review.',
                  'acm': {'principals': ['reader'],
                          'permissions': [['view', 'Deny']]},
                  'display_only_to_roles': ['manager']
                  },
        'announced': {'title': 'Announced',
                      'description': '',
                      'acm': {},
                      },
    },
    'transitions': {
        'to_announced': {'from_state': 'draft',
                         'to_state': 'announced',
                         'callback': None,
                         'permission': 'do_transition',
                         },
    },
}


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, sample_meta, 'sample')
