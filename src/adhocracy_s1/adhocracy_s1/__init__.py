"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory
from adhocracy_core.interfaces import IFixtureAsset


def includeme(config):
    """Setup adhocracy extension."""
    # include adhocracy_core
    config.include('adhocracy_core')
    # commit to allow overriding pyramid config
    config.commit()
    # add translations
    config.add_translation_dirs('adhocracy_core:locale/',
                                'adhocracy_s1:locale/')
    # add extensions
    config.include('.authorization')
    config.include('.catalog')
    config.include('.sheets')
    config.include('.resources')
    config.include('.workflows')
    config.include('.rest')
    config.include('.evolution')
    config.registry.registerUtility('', IFixtureAsset,
                                    name='adhocracy_s1:test_process_fixture')


def main(global_config, **settings):
    """Return a Pyramid WSGI application."""
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
