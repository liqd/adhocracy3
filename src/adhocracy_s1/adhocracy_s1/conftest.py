"""Common fixtures for adhocracy_mercator."""
from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    """Return the adhocracy_s1 test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_s1
    configurator = make_configurator(app_settings, adhocracy_s1)
    return configurator.make_wsgi_app()


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_s1.sheets')
    integration.include('adhocracy_s1.resources')
    integration.include('adhocracy_s1.workflows')
    integration.include('adhocracy_s1.catalog')
    return integration
