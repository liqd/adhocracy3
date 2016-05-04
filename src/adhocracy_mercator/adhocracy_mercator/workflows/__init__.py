"""Workflows for Mercator."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_mercator.workflows:mercator.yaml',
                        'mercator')
    config.add_workflow('adhocracy_mercator.workflows:mercator2.yaml',
                        'mercator2')
