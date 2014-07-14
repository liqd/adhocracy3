"""Simple sample app using the Adhocracy core."""
from adhocracy import root_factory
from pyramid.config import Configurator


def includeme(config):
    """Setup sample app."""
    config.include('adhocracy')
    # include additional default resource types
    config.include('adhocracy.resources.tag')
    config.include('adhocracy.resources.pool')
    config.include('adhocracy.resources.principal')
    # include additional default sheet types
    config.include('adhocracy.sheets.user')
    # include custom resource types
    config.include('adhocracy_sample.resources')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
