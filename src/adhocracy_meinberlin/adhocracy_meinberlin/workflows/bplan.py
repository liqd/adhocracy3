"""Bplan workflow."""


def includeme(config):
    """Add workflow."""
    config.add_workflow('adhocracy_meinberlin.workflows:bplan.yaml',
                        'bplan')
    config.add_workflow('adhocracy_meinberlin.workflows:bplan_private.yaml',
                        'bplan_private')
