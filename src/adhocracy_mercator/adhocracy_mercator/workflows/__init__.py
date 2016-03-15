"""Workflows for Mercator."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_mercator.workflows:mercator.yaml',
                        'mercator')
    config.include('.mercator2')
