"""Resource type configuration."""


def includeme(config):  # pragma: no cover
    """Include all resource types in this package."""
    config.include('.paragraph')
    config.include('.section')
    config.include('.proposal')
    config.include('.comment')
