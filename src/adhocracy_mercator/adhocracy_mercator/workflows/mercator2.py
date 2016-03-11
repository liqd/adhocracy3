"""Workflow for Mercator2."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_mercator.workflows:mercator2.yaml',
                        'mercator2')
