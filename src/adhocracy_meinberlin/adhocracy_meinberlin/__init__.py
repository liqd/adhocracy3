"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy extension."""
    # include adhocracy_core
    config.include('adhocracy_core')
    config.include('adhocracy_core.resources.geo')
    # include sample packages
    # TODO: fix tests and remove
    config.include('adhocracy_core.resources.sample_paragraph')
    config.include('adhocracy_core.resources.sample_section')
    config.include('adhocracy_core.resources.sample_proposal')
    # include custom resource types
    config.include('adhocracy_meinberlin.workflows')
    config.include('adhocracy_meinberlin.resources.kiezkassen')
    config.include('adhocracy_meinberlin.resources.bplan')
    config.include('adhocracy_meinberlin.resources.root')
    config.include('adhocracy_meinberlin.resources.subscriber')
    config.include('adhocracy_meinberlin.sheets.kiezkassen')
    config.include('adhocracy_meinberlin.sheets.bplan')
    config.include('adhocracy_meinberlin.evolution')
    config.add_translation_dirs('adhocracy_core:locale/',
                                'adhocracy_meinberlin:locale/')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
