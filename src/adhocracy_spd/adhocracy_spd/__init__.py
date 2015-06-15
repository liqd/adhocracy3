"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy extension."""
    config.include('adhocracy_sample')
    config.include('.sheets.digital_leben')
    config.include('.workflows.digital_leben')
    config.include('.resources.root')
    config.include('.resources.subscriber')
    config.include('.resources.digital_leben')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
