"""Rest API configuration."""


def includeme(config):  # pragma: no cover
    """Run pyramid configuration."""
    config.include('cornice')
    config.scan('.views')
    config.scan('.exceptions')
