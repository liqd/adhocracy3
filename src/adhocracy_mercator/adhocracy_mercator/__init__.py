"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy extension."""
    # include adhocracy_core
    config.include('adhocracy_core')
    # include custom resource types
    config.include('adhocracy_core.resources.sample_paragraph')
    config.include('adhocracy_core.resources.sample_section')
    config.include('adhocracy_core.resources.sample_proposal')
    config.include('.catalog')
    config.include('.sheets.mercator')
    config.include('.resources.root')
    config.include('.resources.mercator')
    config.include('.resources.subscriber')
    config.include('.evolution')
    config.add_translation_dirs('adhocracy_core:locale/')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    app = config.make_wsgi_app()
    return app
