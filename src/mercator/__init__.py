"""Adhocracy frontend customization for Mercator."""
from pyramid.config import Configurator

from adhocracy_frontend import add_frontend_route


def includeme(config):
    """Setup adhocracy frontend extension."""
    # include adhocracy_frontend
    config.include('adhocracy_frontend')
    # override static javascript and css files
    config.override_asset(to_override='adhocracy_frontend:build/',
                          override_with='mercator:build/')
    add_frontend_route(config, 'mercator', 'mercator')
    add_frontend_route(config, 'mercator-listing', 'mercator-listing')
    add_frontend_route(config, 'mercator-detail', 'mercator-detail')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings)
    includeme(config)
    app = config.make_wsgi_app()
    return app
