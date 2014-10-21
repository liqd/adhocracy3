"""Adhocracy backend server with default content and settings."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup sample app."""
    # include adhocracy_core
    config.include('adhocracy_mercator')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    app = config.make_wsgi_app()
    return app
