"""Adhocracy backend server with default content and settings."""
from pyramid.config import Configurator

from adhocracy_core import root_factory


def includeme(config):
    """Setup sample app."""
    # include adhocracy_core
    config.include('adhocracy_core')
    # include custom resource types
    config.include('adhocracy_core.resources.sample_paragraph')
    config.include('adhocracy_core.resources.sample_section')
    config.include('adhocracy_core.resources.sample_proposal')
    config.include('adhocracy_core.sheets.mercator')
    config.include('adhocracy_core.resources.mercator')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    app = config.make_wsgi_app()
    warm_up_database(app)
    return app


def warm_up_database(app):
    """Fill the zodb connection pool to make the application start faster."""
    # FIXME This makes not much sense for really big databases
    from pyramid import testing
    from adhocracy_core.interfaces import IResource
    from adhocracy_core.rest.views import ResourceRESTView
    request = testing.DummyRequest()
    request.registry = app.registry
    request.validated = {}
    request.errors = []
    root = app.root_factory(request)
    # warm up reference map
    om = root.__objectmap__
    [x for x in om.referencemap.refmap.values()]
    [x for x in om.referencemap.refmap.keys()]
    # warm up all resources in the database
    resolve = om.object_for
    resources = [resolve(p) for p in om.pathlookup(('',))]
    for resource in [r for r in resources if IResource.providedBy(r)]:
        view = ResourceRESTView(resource, request)
        appstruct = view.get()
        del appstruct
