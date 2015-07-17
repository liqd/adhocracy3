"""Configure rest api packages."""


def includeme(config):  # pragma: no cover
    """Include all rest views configuration."""
    config.include('.views')
    config.include('.batchview')
    config.add_request_method(lambda x: [], name='errors', reify=True)
    config.add_request_method(lambda x: {}, name='validated', reify=True)
    config.include('.exceptions')
    config.include('.subscriber')
