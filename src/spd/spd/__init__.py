"""Adhocracy extension."""
from pyramid.config import Configurator
from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy frontend extension."""
    # include core adhocracy and backend customizations
    config.include('adhocracy_spd')
    config.include('adhocracy_frontend')
    # extend default config
    config.config_defaults('spd:defaults.yaml')
    # override static javascript and css files
    config.override_asset(to_override='adhocracy_frontend:build/',
                          override_with='spd:build/')


def main(global_config, **settings):
    """Return a Pyramid WSGI application."""
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    app = config.make_wsgi_app()
    return app
