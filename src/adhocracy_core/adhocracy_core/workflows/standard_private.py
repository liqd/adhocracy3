"""Private standard workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_core.workflows:standard_private.yaml',
                        'standard_private')
