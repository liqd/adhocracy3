"""Private debate workflow."""

# flake8: noqa
from functools import partial

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows import match_permission
from adhocracy_core.workflows.debate import debate_meta

match = partial(match_permission, debate_meta)

debate_private_meta =  debate_meta \
                .transform(('states', 'announce', 'acm', 'permissions', match('announce', 'view')),
                          # 'principals': ['anonymous',  'participant', 'moderator', 'creator', 'initiator', 'admin'],
                          ['view',         'Deny',       'Allow',       'Allow',     'Allow',   'Allow',      None])   \
                .transform(('states', 'participate', 'acm', 'permissions', match('participate', 'view')),
                           ['view',        'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'evaluate', 'acm', 'permissions', match('evaluate', 'view')),
                           ['view',        'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'result', 'acm', 'permissions', match('result', 'view')),
                           ['view',        'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'closed', 'acm', 'permissions', match('closed', 'view')),
                           ['view',        'Deny',        None,         None,          None,      None,       None])

def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, debate_private_meta, 'debate_private')
