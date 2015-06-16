"""Resource type configuration and default factory."""


def includeme(config):
    """Include resource types and subscribers."""
    config.include('.root')
    config.include('.mercator')
    config.include('.subscriber')
