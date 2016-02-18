"""Common fixtures for adhocracy_euth."""
from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_euth
    configurator = make_configurator(app_settings, adhocracy_euth)
    return configurator.make_wsgi_app()


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_euth.resources')
    return integration
