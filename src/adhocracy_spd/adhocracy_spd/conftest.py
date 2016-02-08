"""Common fixtures for adhocracy_mercator."""
from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    """Return the adhocracy_spd test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_spd
    configurator = make_configurator(app_settings, adhocracy_spd)
    return configurator.make_wsgi_app()


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_spd.sheets')
    integration.include('adhocracy_spd.resources')
    integration.include('adhocracy_spd.workflows')
    return integration
