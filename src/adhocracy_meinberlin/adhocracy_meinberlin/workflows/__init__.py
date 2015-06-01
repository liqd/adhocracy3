"""Workflows for myberlin."""


def includeme(config):  # pragma: no cover
    """Include workflows."""
    config.include('.kiezkassen')
    config.include('.bplan')
