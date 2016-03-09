"""Common test fixtures."""
from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_meinberlin
    configurator = make_configurator(app_settings, adhocracy_meinberlin)
    return configurator.make_wsgi_app()


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_meinberlin.workflows')
    integration.include('adhocracy_meinberlin.sheets')
    integration.include('adhocracy_meinberlin.resources')
    integration.include('adhocracy_meinberlin.workflows')
    integration.include('adhocracy_meinberlin.content')
    return integration
