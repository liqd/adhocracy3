"""Send runtime statistics to `statsd <http://statsd.readthedocs.org>`."""


def includeme(config):
    """Add statsd client."""
    config.include('substanced.stats')
    config.include('.subscriber')
