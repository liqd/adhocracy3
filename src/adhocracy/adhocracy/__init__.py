"""Setup pyramid wsgi app."""
from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from pyramid.authorization import ACLAuthorizationPolicy
from substanced.evolution import mark_unfinished_as_finished as markunf
import transaction

from adhocracy.authentication import TokenHeaderAuthenticationPolicy
from adhocracy.resources.root import IRootPool


def root_factory(request, t=transaction, g=get_connection,
                 mark_unfinished_as_finished=False):
    """ A function which can be used as a Pyramid ``root_factory``.

    It accepts a request and returns an instance of the ``Root`` content type.

    """
    # FIXME: Fix substanced bug: mark_unfinished_as_finished keyword
    # is not working.
    # Don't get the root object if the request already has one.
    # Workaround to make the subrequests in adhocracy.rest.batchview work.
    if getattr(request, 'root', False):
        return request.root
    conn = g(request)
    zodb_root = conn.root()
    if 'app_root' not in zodb_root:
        registry = request.registry
        app_root = registry.content.create(IRootPool.__identifier__)
        zodb_root['app_root'] = app_root
        t.savepoint()  # give app_root a _p_jar
        if mark_unfinished_as_finished:
            markunf(app_root, registry, t)
        t.commit()
    add_after_commit_hooks(request)
    return zodb_root['app_root']


def add_after_commit_hooks(request):
    """Add after commit hook to notify the websocket server."""
    # FIXME this is a quick hack
    from adhocracy.websockets.client import send_messages_after_commit_hook
    from adhocracy.resources.subscriber import\
        clear_transaction_changelog_after_commit_hook
    current_transaction = transaction.get()
    registry = request.registry
    current_transaction.addAfterCommitHook(send_messages_after_commit_hook,
                                           args=(registry,))
    current_transaction.addAfterCommitHook(
        clear_transaction_changelog_after_commit_hook, args=(registry,))


def includeme(config):
    """Setup basic adhocracy."""
    settings = config.registry.settings
    config.include('pyramid_zodbconn')
    config.include('pyramid_mailer')
    config.include('pyramid_exclog')
    config.hook_zca()  # enable global adapter lookup (used by adhocracy.utils)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    authn_secret = settings.get('substanced.secret')
    authn_timeout = 60 * 60 * 24 * 30
    authn_policy = TokenHeaderAuthenticationPolicy(authn_secret,
                                                   timeout=authn_timeout)
    config.set_authentication_policy(authn_policy)
    config.include('.authentication')
    config.include('.subscriber')
    config.include('.evolution')
    config.include('.events')
    config.include('.subscriber')
    config.include('.registry')
    config.include('.graph')
    config.include('.catalog')
    config.include('.sheets')
    config.include('.resources.pool')
    config.include('.resources.root')
    config.include('.resources.tag')
    config.include('.resources.principal')
    config.include('.resources.subscriber')
    config.include('.websockets')
    config.include('.rest')
    config.include('.frontend')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings, root_factory=root_factory)
    includeme(config)
    return config.make_wsgi_app()
