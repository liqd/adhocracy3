from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from substanced import root_factory


def includeme(config):
    """Setup basic adhocracy."""
    # FIXME: Fix substanced.sdi bug: you need to register the authorisation utility first,
    # then the auhentication.
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    # now we can proceed
    config.include('substanced')
    config.commit()  # commit to allow proper config overrides
    config.include('.properties')
    config.include('.resources')
    #config.include('.registry')
    config.include('.evolution')
    #config.include('.rest')
    config.include('.frontend')
    config.scan()


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
