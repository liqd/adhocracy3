"""Stadtforum workflows."""

# flake8: noqa

from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

stadtforum_meta = standard_meta \
                 .transform(('states', 'participate', 'acm'),
                            {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                             'permissions':
                             [['create_proposal',               None,          None,        None,     'Allow'],
                              ['edit_proposal',                 None,          None,       'Allow',    None]
                             ]})

stadtforum_poll_meta = standard_meta \
                       .transform(('states', 'participate', 'acm'),
                                  {'principals':                    ['participant', 'moderator', 'creator', 'initiator'],
                                   'permissions':
                                   [['create_proposal',               None,          None,        None,      None],
                                    ['edit_proposal',                 None,          None,        None,      None],
                                    ['create_comment',               'Allow',       'Allow',      None,      None],
                                    ['edit_comment',                  None,          None,       'Allow',    None],
                                    ['create_rate',                  'Allow',        None,        None,      None],
                                    ['edit_rate',                     None,          None,       'Allow',    None],
                                    ['create_relation',              'Allow',        None,        None,      None],
                                    ['edit_relation',                 None,          None,       'Allow',    None]
                                   ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, stadtforum_meta, 'stadtforum')
    add_workflow(config.registry, stadtforum_poll_meta, 'stadtforum_poll')
