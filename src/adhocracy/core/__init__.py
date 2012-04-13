from pyramid.config import Configurator

from adhocracy.core.models import utilities
from adhocracy.core.models.adhocracyroot import appmaker
from adhocracy.core.models.interfaces import IGraphConnection


def root_factory(request):
    """Return application root
    """
    graph = request.registry.getUtility(IGraphConnection)

    return appmaker(graph)

def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    #load application settings
    config = Configurator(root_factory=root_factory, settings=settings)
    #hook zope global component registry into the pyramid application registry
    #http://docs.pylonsproject.org/projects/pyramid/en/1.3-branch/narr/zca.html?highlight=utility#using-the-zca-global-registry
    config.hook_zca()
    #add views (TODO: use zcml or imperative?)
    config.add_static_view('static', 'static', cache_max_age=3600)
    #scan modules for configurations decorators
    config.scan()
    #load zcml configuration files
    #http://readthedocs.org/docs/pyramid_zcml/en/latest/narr.html
    config.include('pyramid_zcml')
    config.load_zcml('configure.zcml')

    return config.make_wsgi_app()

