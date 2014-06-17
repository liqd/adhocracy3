"""Public py.test fixtures."""

import pytest


@pytest.fixture()
def app_adhocracy_sample(config):
    """Return the adhocracy wsgi application."""
    from adhocracy_sample import includeme
    includeme(config)
    return config.make_wsgi_app()