"""Workflows for Mercator."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

mercator_meta = standard_meta \
                .transform(('states', 'participate', 'acm'),
                           {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                            'permissions':
                            [['create_mercator_proposal',     'Allow',        None,        None,     'Allow'],
                             ['edit_mercator_proposal',        None,          None,       'Allow',    None],
                             ['create_comment',               'Allow',       'Allow',      None,     'Allow'],
                             ['edit_comment',                  None,          None,       'Allow',    None],
                             ['create_rate',                  'Allow',        None,        None,      None],
                             ['edit_rate',                     None,          None,       'Allow',    None],
                            ]}) \
                .transform(('states', 'evaluate', 'acm'),
                           {'principals':                      ['participant', 'moderator', 'creator', 'initiator'],
                            'permissions':
                            [['create_mercator_proposal',        None,          None,        None,      'Allow'],
                             ['edit_mercator_proposal',          None,          None,        None,      'Allow'],
                            ]}) \
                .transform(('states', 'result', 'acm'),
                           {'principals':                      ['participant', 'moderator', 'creator', 'initiator'],
                            'permissions':
                            [['create_mercator_proposal',        None,          None,        None,      'Allow'],
                             ['edit_mercator_proposal',          None,          None,       'Allow',    'Allow'],
                             ['create_document',                 None,          None,       'Allow',    'Allow'],
                             ['edit_document',                   None,          None,       'Allow',    'Allow'],
                            ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, mercator_meta, 'mercator')
    config.include('.mercator2')
