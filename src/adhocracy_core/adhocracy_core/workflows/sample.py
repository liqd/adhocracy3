"""Example workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_core.workflows:sample.yaml', 'sample')
