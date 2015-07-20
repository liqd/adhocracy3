"""Digital leben workflow."""
from adhocracy_core.workflows import add_workflow
from adhocracy_core.workflows.standard import standard_meta

digital_leben_meta =  standard_meta \
                      .transform(('states', 'participate', 'acm'),
                                 {'principals': [                   'participant', 'moderator', 'creator', 'initiator'],  # noqa
                                'permissions':
                                  [['create_proposal',             None,          None,        None,     'Allow'],  # noqa
                                   ['edit_proposal',               None,          None,       'Allow',   'Allow'],  # noqa
                                   ['create_comment',             'Allow',       'Allow',      None,     'Allow'],  # noqa
                                   ['edit_comment',                None,          None,       'Allow',    None  ],  # noqa
                                   ['create_rate',                'Allow',        None,        None,      None  ],  # noqa
                                   ['edit_rate',                   None,          None,       'Allow',    None  ],  # noqa
                                   ]})


def includeme(config):
    """Add workflow."""
    add_workflow(config.registry, digital_leben_meta, 'digital_leben')
