"""Adhocracy extension."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup adhocracy extension.

    The kit package should be exactly like the spd package but with different
    root permissions and default translations for the emails.
    """
    # copied from adhocracy_spd (without resources and translations)
    config.include('adhocracy_core')
    config.commit()
    config.include('adhocracy_spd.sheets')
    config.include('adhocracy_spd.workflows')
    config.include('adhocracy_spd.evolution')

    # add translations
    config.add_translation_dirs('adhocracy_core:locale/')

    # copoied from adhocracy_spd.resources resources
    config.include('adhocracy_spd.resources.digital_leben')

    # include kit resource types
    config.include('.resources')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
