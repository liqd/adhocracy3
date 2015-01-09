"""Frontend view and simple pyramid app configurations."""
import pkg_resources

from pyramid.config import Configurator
from pyramid.events import NewResponse
from pyramid.request import Request
from pyramid.response import FileResponse
from pyramid.settings import aslist

from adhocracy_core.rest.views import add_cors_headers_subscriber


def config_view(request):
    """Return the frontend configuration."""
    settings = request.registry.settings or {}
    config = {}
    if 'adhocracy.frontend.ws_url' in settings:
        public_ws_url = settings.get('adhocracy.frontend.ws_url')
    else:
        public_ws_url = _build_ws_url(request)
    config['ws_url'] = public_ws_url
    config['rest_url'] = settings.get('adhocracy.frontend.rest_url',
                                      'http://localhost:6541')
    config['canonical_url'] = settings.get('adhocracy.canonical_url',
                                           'http://localhost:6551')
    platform_id = settings.get('adhocracy.platform_id', 'adhocracy')
    config['rest_platform_path'] = '/{}/'.format(platform_id)
    config['pkg_path'] = settings.get('adhocracy.frontend.pkg_path',
                                      '/static/js/Packages')
    config['trusted_domains'] = aslist(
        settings.get('adhocracy.trusted_domains', []))
    config['support_email'] = settings.get('adhocracy.frontend.support_email',
                                           'support@unconfigured.domain')
    config['locale'] = settings.get('adhocracy.frontend.locale', 'en')
    custom_keys = settings.get('adhocracy.custom', '').split()
    config['custom'] = {k: settings.get('adhocracy.custom.%s' % k)
                        for k in custom_keys}
    config['site_name'] = settings.get('adhocracy.frontend.site_name',
                                       'Adhocracy')
    return config


def root_view(request):
    """Return the embeddee HTML."""
    path = pkg_resources.resource_filename('adhocracy_frontend',
                                           'build/root.html')
    return FileResponse(path, request=request)


def _build_ws_url(request: Request) -> str:
    ws_domain = request.domain
    ws_port = 8080
    ws_scheme = 'wss' if request.scheme == 'https' else 'ws'
    return '{}://{}:{}'.format(ws_scheme, ws_domain, ws_port)


def includeme(config):
    """Add routing and static view to deliver the frontend application."""
    config.add_static_view('static', 'adhocracy_frontend:build/',
                           cache_max_age=0)
    config.add_route('config_json', 'config.json')
    config.add_view(config_view, route_name='config_json', renderer='json',
                    http_cache=0)
    add_frontend_route(config, 'embed', 'embed/{directive}')
    add_frontend_route(config, 'register', 'register')
    add_frontend_route(config, 'login', 'login')
    add_frontend_route(config, 'activate', 'activate/{key}')
    add_frontend_route(config, 'activation_error', 'activation_error')
    add_frontend_route(config, 'root', '')
    add_frontend_route(config, 'resource', 'r/*path')
    config.add_subscriber(add_cors_headers_subscriber, NewResponse)


def add_frontend_route(config, name, pattern):
    """Add view and route to adhocracy frontend."""
    config.add_route(name, pattern)
    config.add_view(root_view, route_name=name, renderer='html', http_cache=0)


def main(global_config, **settings):
    """ Return a Pyramid WSGI application to serve the frontend application."""
    config = Configurator(settings=settings)
    includeme(config)
    return config.make_wsgi_app()
