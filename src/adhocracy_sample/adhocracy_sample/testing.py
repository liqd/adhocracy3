"""Public py.test fixtures."""
from pytest import fixture


@fixture(scope='class')
def app_sample(zeo, settings, websocket):
    """Return the adhocracy sample wsgi application."""
    from pyramid.config import Configurator
    import adhocracy_sample
    configurator = Configurator(settings=settings,
                                root_factory=adhocracy_sample.root_factory)
    configurator.include(adhocracy_sample)
    return configurator.make_wsgi_app()
