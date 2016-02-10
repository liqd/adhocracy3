"""Common fixtures for adhocracy_mercator."""
from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_mercator
    configurator = make_configurator(app_settings, adhocracy_mercator)
    return configurator.make_wsgi_app()


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_mercator.sheets')
    integration.include('adhocracy_mercator.resources')
    integration.include('adhocracy_mercator.catalog')
    integration.include('adhocracy_mercator.workflows')
    return integration
