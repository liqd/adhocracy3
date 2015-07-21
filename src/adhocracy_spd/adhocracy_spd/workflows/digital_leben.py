"""Digital leben workflow."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

digital_leben_meta =  standard_meta \
                      .transform(('states', 'participate', 'acm'),
                                 {'principals': [                 'participant', 'moderator', 'creator', 'initiator'],
                                  'permissions':
                                  [['create_proposal',             None,          None,        None,     'Allow'],
                                   ['edit_proposal',               None,          None,       'Allow',   'Allow'],
                                   ['create_comment',             'Allow',       'Allow',      None,     'Allow'],
                                   ['edit_comment',                None,          None,       'Allow',    None  ],
                                   ['create_rate',                'Allow',        None,        None,      None  ],
                                   ['edit_rate',                   None,          None,       'Allow',    None  ],
                                  ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, digital_leben_meta, 'digital_leben')
