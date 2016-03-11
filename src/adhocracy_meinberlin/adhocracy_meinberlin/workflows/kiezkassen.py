"""Kiezkassen workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_meinberlin.workflows:kiezkassen.yaml',
                        'kiezkassen')
