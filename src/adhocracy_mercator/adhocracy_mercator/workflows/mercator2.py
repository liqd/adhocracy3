"""Workflow for Mercator2."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

mercator2_meta = standard_meta \
                 .transform(('states', 'participate', 'acm'),
                            {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                             'permissions':
                             [['create_proposal',              'Allow',        None,        None,     'Allow'],
                              ['edit_proposal',                 None,          None,       'Allow',    None],
                              ['create_comment',               'Allow',       'Allow',      None,     'Allow'],
                              ['edit_comment',                  None,          None,       'Allow',    None],
                              ['create_rate',                  'Allow',        None,        None,      None],
                              ['edit_rate',                     None,          None,       'Allow',    None],
                              ['create_badge_assignment',      'Allow',        None,        None,      None],
                              ['view_mercator2_extra_funding', 'Deny',        'Allow',     'Allow',    None],
                              ['view_mercator2_winnerinfo',    'Deny',        'Deny',       None,      None],
                              ['edit_mercator2_winnerinfo',    'Deny',        'Deny',       None,      None]
                             ]}) \
                 .transform(('states', 'evaluate', 'acm'),
                            {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                             'permissions':
                             [['edit',                          None,          None,       'Deny',     None],
                              ['view_mercator2_extra_funding', 'Deny',        'Allow',      None,      None],
                              ['view_mercator2_winnerinfo',    'Deny',        'Allow',      None,      None],
                              ['edit_mercator2_winnerinfo',    'Deny',        'Allow',      None,      None]
                             ]}) \
                 .transform(('states', 'result', 'acm'),
                            {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                             'permissions':
                             [['edit',                          None,          None,       'Allow',    None],
                              ['edit_proposal',                 None,          None,       'Allow',    None],
                              ['view_mercator2_extra_funding', 'Deny',        'Allow',      None,      None],
                              ['view_mercator2_winnerinfo',    'Allow',       'Allow',      None,      None],
                              ['edit_mercator2_winnerinfo',    'Deny',        'Allow',      None,      None],
                              ['create_document',               None,          None,       'Allow',    None],
                              ['edit_document',                 None,          None,       'Allow',    None],
                             ]}) \
                 .transform(('states', 'closed', 'acm'),
                            {'principals':                      ['participant', 'moderator', 'creator', 'initiator'],
                             'permissions':
                             [['edit',                            None,          None,       'Deny',     None],
                             ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, mercator2_meta, 'mercator2')
