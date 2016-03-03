"""Workaround to force fixture override for doctest."""
from pytest import fixture


@fixture(scope='class', autouse=True)  # autouse needed to make the doctest run
def app_router(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from adhocracy_core.testing import make_configurator
    import adhocracy_meinberlin
    configurator = make_configurator(app_settings, adhocracy_meinberlin)
    return configurator.make_wsgi_app()
