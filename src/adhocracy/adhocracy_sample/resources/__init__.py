"""Resource type configuration."""


def includeme(config):
    """Include all resource types in this package."""
    config.include('.paragraph')
    config.include('.section')
    config.include('.proposal')
