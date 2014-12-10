"""Common fixtures for adhocracy_mercator."""
from pytest import fixture


@fixture(scope='class')
def app(app_settings):
    """Return the adhocracy_mercator test wsgi application."""
    from pyramid.config import Configurator
    from adhocracy_core.testing import includeme_root_with_test_users
    import adhocracy_mercator
    configurator = Configurator(settings=app_settings,
                                root_factory=adhocracy_mercator.root_factory)
    configurator.include(adhocracy_mercator)
    configurator.commit()
    configurator.include(includeme_root_with_test_users)
    app = configurator.make_wsgi_app()
    return app
