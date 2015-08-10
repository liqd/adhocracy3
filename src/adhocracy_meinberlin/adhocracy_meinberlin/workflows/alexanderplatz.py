"""Alexanderplatz workflow."""

# flake8: noqa


from pyrsistent import freeze

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

alexanderplatz_meta = standard_meta \
             .transform(('states', 'announce', 'acm'),
                        {'principals':                    ['anonymous', 'moderator', 'participant', 'creator', 'initiator'],
                         'permissions':
                         [['view',                         'Deny',      'Allow',     'Deny',        'Allow',   'Allow'],
                           ['create_document',              None,       'Allow',      None,          None,      None],
                           ['edit_document',                None,       'Allow',      None,         'Allow',    None],
                          ]}) \
             .transform(('states', 'participate', 'acm'),
                        {'principals':                    ['moderator', 'participant', 'creator', 'initiator'],
                         'permissions':
                         [['create_proposal',               None,       'Allow',        None,      None],
                          ['edit_proposal',                 None,        None,         'Allow',    None],
                          ['create_document' ,             'Allow',      None,          None,      None],
                          ['edit_document',                'Allow',      None,          None,      None],
                          ['create_comment',               'Allow',     'Allow',        None,      None],
                          ['edit_comment',                  None,        None,         'Allow',    None],
                          ['create_rate',                  'Allow',      None,          None,      None],
                          ['edit_rate',                     None,        None,         'Allow',    None],
                         ]}) \
             .transform(('states', 'evaluate', 'acm'),
                        {'principals':                    ['moderator', 'participant', 'creator', 'initiator'],
                         'permissions':
                         [['create_proposal',               None,        None,          None,      None],
                          ['edit_proposal',                 None,        None,          None,      None],
                          ['create_document' ,             'Allow',      None,          None,      None],
                          ['edit_document',                'Allow',      None,          None,      None],
                          ['create_comment',               'Allow',     'Allow',        None,      None],
                          ['edit_comment',                  None,        None,         'Allow',    None],
                         ]}) \
             .transform(('states', 'result', 'acm'),
                        {'principals':                    ['moderator', 'participant', 'creator', 'initiator'],
                         'permissions':
                         [['create_proposal',               None,        None,          None,      None],
                          ['edit_proposal',                 None,        None,          None,      None],
                          ['create_document' ,             'Allow',      None,          None,      None],
                          ['edit_document',                'Allow',      None,          None,      None],
                          ['create_comment',               'Allow',      None,          None,      None],
                          ['edit_comment',                  None,        None,         'Allow',    None],
                         ]})

def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, alexanderplatz_meta, 'alexanderplatz')
