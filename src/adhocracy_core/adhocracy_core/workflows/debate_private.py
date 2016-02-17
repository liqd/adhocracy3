"""Private debate workflow."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

# TODO refactor
def view_matcher(idx):
    return standard_meta['states']['participate']['acm']['permissions'][idx][0] \
        == 'view'

debate_private_meta =  standard_meta \
               .transform(('states', 'participate', 'acm', 'permissions', view_matcher),
                          # 'principals': [                 'anonymous',  'participant', 'moderator', 'creator', 'initiator'],
                          ['view',                          'Deny',       'Allow',       'Allow',     'Allow',   'Allow'])
# TODO: specify result state and other states

def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, debate_private_meta, 'debate_private')
