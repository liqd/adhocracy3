from pyramid.config import Configurator
from substanced import root_factory



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)
    config.include('substanced')
    config.commit() # commit to allow proper config overrides
    config.include('.propertysheets')
    config.include('.contentregistry')
    config.include('.evolution')
    config.include('.rest')
    config.scan()

    return config.make_wsgi_app()

