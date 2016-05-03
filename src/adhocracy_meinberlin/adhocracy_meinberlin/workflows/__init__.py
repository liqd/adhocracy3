"""Workflows for myberlin."""


def includeme(config):  # pragma: no cover
    """Include workflows."""
    config.add_workflow('adhocracy_meinberlin.workflows:kiezkassen.yaml',
                        'kiezkassen')
    config.add_workflow('adhocracy_meinberlin.workflows:bplan.yaml',
                        'bplan')
    config.add_workflow('adhocracy_meinberlin.workflows:bplan_private.yaml',
                        'bplan_private')
    config.add_workflow('adhocracy_meinberlin.workflows:alexanderplatz.yaml',
                        'alexanderplatz')
    config.add_workflow('adhocracy_meinberlin.workflows:stadtforum.yaml',
                        'stadtforum')
    config.add_workflow('adhocracy_meinberlin.workflows:stadtforum_poll.yaml',
                        'stadtforum_poll')
