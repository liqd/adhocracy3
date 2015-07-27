"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy extension."""
    # include adhocracy_core
    config.include('adhocracy_core')
    # commit to allow overriding pyramid config
    config.commit()
    # include custom resource types
    config.include('adhocracy_meinberlin.workflows')
    config.include('adhocracy_meinberlin.resources')
    config.include('adhocracy_meinberlin.sheets')
    config.include('adhocracy_meinberlin.evolution')
    config.add_translation_dirs('adhocracy_core:locale/',
                                'adhocracy_meinberlin:locale/')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
