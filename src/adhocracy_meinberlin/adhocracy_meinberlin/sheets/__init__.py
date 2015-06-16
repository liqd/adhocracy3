"""Adhocracy sheets."""


def includeme(config):  # pragma: no cover
    """Include sheets."""
    config.include('.kiezkassen')
    config.include('.bplan')
