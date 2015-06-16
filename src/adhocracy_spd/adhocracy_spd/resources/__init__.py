"""Resource type configuration and default factory."""


def includeme(config):
    """Include resource types and subscribers."""
    config.include('.digital_leben')
    config.include('.root')
    config.include('.subscriber')
