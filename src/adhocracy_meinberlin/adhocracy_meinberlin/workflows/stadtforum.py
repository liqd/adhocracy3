"""Stadtforum workflows."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_meinberlin.workflows:stadtforum.yaml',
                        'stadtforum')
    config.add_workflow('adhocracy_meinberlin.workflows:stadtforum_poll.yaml',
                        'stadtforum_poll')
