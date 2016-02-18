"""Private standard workflow."""

# flake8: noqa

from functools import partial

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows import match_permission
from adhocracy_core.workflows.standard import standard_meta

match = partial(match_permission, standard_meta)

standard_private_meta =  standard_meta \
                .transform(('states', 'announce', 'acm', 'permissions', match('announce', 'view')),
                           # 'principals': ['anonymous',  'participant', 'moderator', 'creator', 'initiator', 'admin'],
                          ['view',          'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'participate', 'acm', 'permissions', match('participate', 'view')),
                          ['view',          'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'evaluate', 'acm', 'permissions', match('evaluate', 'view')),
                          ['view',          'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'result', 'acm', 'permissions', match('result', 'view')),
                          ['view',          'Deny',        None,         None,          None,      None,       None]) \
                .transform(('states', 'closed', 'acm', 'permissions', match('closed', 'view')),
                          ['view',          'Deny',        None,         None,          None,      None,       None])

def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, standard_private_meta, 'standard_private')
