"""Alexanderplatz workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_meinberlin.workflows:alexanderplatz.yaml',
                        'alexanderplatz')
