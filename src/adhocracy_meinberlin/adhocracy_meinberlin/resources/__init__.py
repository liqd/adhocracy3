"""Resource type configuration and default factory."""


def includeme(config):
    """Include resource types and subscribers."""
    config.include('.kiezkassen')
    config.include('.bplan')
    config.include('.root')
    config.include('.subscriber')
