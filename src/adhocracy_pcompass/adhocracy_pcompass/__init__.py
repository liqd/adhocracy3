"""Adhocracy extension."""
from pyramid.config import Configurator
from adhocracy_core import root_factory


def includeme(config):  # pragma: no cover
    """Setup adhocracy extension."""
    config.include('adhocracy_core')
    config.include('.resources')
    config.add_translation_dirs('adhocracy_core:locale/',
                                'adhocracy_pcompass:locale/')


def main(global_config, **settings):  # pragma: no cover
    """Return a Pyramid WSGI application."""
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
