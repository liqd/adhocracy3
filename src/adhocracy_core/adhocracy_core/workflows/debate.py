"""Debate workflow."""

# flake8: noqa
from pyrsistent import freeze

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

debate_meta = standard_meta \
              .transform(('states', 'participate', 'acm'),
                         freeze(
                         {'principals': [                 'anonymous',  'participant', 'moderator', 'creator', 'initiator', 'admin'],
                          'permissions':
                          [['view',                        None,        'Allow',       'Allow',     'Allow',   'Allow',      None],
                           ['create_proposal',             None,         None,          None,        None,     'Allow',      None],
                           ['edit_proposal',               None,         None,          None,       'Allow',   'Allow',      None],
                           ['create_document',             None,         None,          None,        None,     'Allow',      None],
                           ['edit_document',               None,         None,          None,       'Allow',   'Allow',      None],
                           ['create_comment',              None,        'Allow',       'Allow',      None,     'Allow',      None],
                           ['edit_comment',                None,         None,          None,       'Allow',    None,        None],
                           ['create_rate',                 None,        'Allow',        None,        None,      None,        None],
                           ['edit_rate',                   None,         None,          None,       'Allow',    None,        None],
                          ]}))

def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, debate_meta, 'debate')
