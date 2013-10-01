import transaction
from pyramid_zodbconn import get_connection
from pyramid.config import Configurator
from substanced import root_factory
from substanced.stats import statsd_incr


def root_factory(request, t=transaction, g=get_connection,
                 mark_unfinished_as_finished=False):
    """ A function which can be used as a Pyramid ``root_factory``.  It
    accepts a request and returns an instance of the ``Root`` content type."""
    # accepts "t", "g", and "mark_unfinished_as_finished" for unit testing
    # purposes only
    conn = g(request)
    zodb_root = conn.root()
    if not 'app_root' in zodb_root:
        registry = request.registry
        app_root = registry.content.create('Root')
        zodb_root['app_root'] = app_root
        t.savepoint() # give app_root a _p_jar
        if mark_unfinished_as_finished:
            mark_unfinished_as_finished(app_root, registry, t)
        t.commit()
    statsd_incr('root_factory', rate=.1)
    return zodb_root['app_root']


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)
    config.include('substanced')
    config.commit() # commit to allow proper config overrides
    config.include('.propertysheets')
    config.include('.contents')
    config.include('.contentregistry')
    config.include('.evolution')
    config.include('.rest')

    config.include('.frontend')

    config.scan()

    return config.make_wsgi_app()

