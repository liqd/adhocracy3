"""Setup pyramid wsgi app."""
from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from pyramid.authorization import ACLAuthorizationPolicy
from substanced.evolution import mark_unfinished_as_finished as markunf

import transaction


def root_factory(request, t=transaction, g=get_connection,
                 mark_unfinished_as_finished=False):  # pragma: no cover
    """ A function which can be used as a Pyramid ``root_factory``.

    It accepts a request and returns an instance of the ``Root`` content type.

    """
    #FIXME: Fix substanced bug: mark_unfinished_as_finished keyqord
    # is not working
    conn = g(request)
    zodb_root = conn.root()
    if not 'app_root' in zodb_root:
        registry = request.registry
        app_root = registry.content.create('Root')
        zodb_root['app_root'] = app_root
        t.savepoint()  # give app_root a _p_jar
        if mark_unfinished_as_finished:  # pragma: no cover
            markunf(app_root, registry, t)
        t.commit()
    return zodb_root['app_root']


def includeme(config):  # pragma: no cover
    """Setup basic adhocracy."""
    # FIXME: Fix substanced.sdi bug: you need to register the authorisation
    # utility first, # then the auhentication.
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    # now we can proceed
    config.include('substanced')
    config.commit()  # commit to allow proper config overrides
    config.include('.sheets')
    # By default there are now resource types included.
    # Your extension package needs to explicit include them.
    # config.include('.resources.tag')
    # config.include('.resources.pool')
    config.include('.events')
    config.include('.subscriber')
    config.include('.registry')
    config.include('.evolution')
    config.include('.graph')
    config.include('.rest')
    config.include('.frontend')


def main(global_config, **settings):  # pragma: no cover
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
