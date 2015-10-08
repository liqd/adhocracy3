"""Resource type configuration."""


def includeme(config):
    """Include resource types."""
    config.include('.request')
    config.include('.subscriber')
