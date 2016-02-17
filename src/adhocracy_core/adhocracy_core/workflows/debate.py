"""Debate workflow."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

debate_meta =  standard_meta \
               .transform(('states', 'participate', 'acm'),
                          {'principals': [                 'anonymous',  'participant', 'moderator', 'creator', 'initiator'],
                           'permissions':
                           [['view',                        None,        'Allow',       'Allow',     'Allow',   'Allow'],
                            ['create_proposal',             None,         None,          None,        None,     'Allow'],
                            ['edit_proposal',               None,         None,          None,       'Allow',   'Allow'],
                            ['create_document',             None,         None,          None,        None,     'Allow'],
                            ['edit_document',               None,         None,          None,       'Allow',   'Allow'],
                            ['create_comment',              None,        'Allow',       'Allow',      None,     'Allow'],
                            ['edit_comment',                None,         None,          None,       'Allow',    None  ],
                            ['create_rate',                 None,        'Allow',        None,        None,      None  ],
                            ['edit_rate',                   None,         None,          None,       'Allow',    None  ],
                           ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, debate_meta, 'debate')
