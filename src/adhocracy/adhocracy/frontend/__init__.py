"""Frontend view and simple pyramid app configurations."""
from urllib.parse import urlparse
import os

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import FileResponse


def config_view(request):
    """Return the frontend configuration."""
    settings = request.registry.settings or {}
    config = {}
    internal_ws_url = settings.get('adhocracy.ws_url', '')
    if 'adhocracy.frontend.ws_url' in settings:
        public_ws_url = settings.get('adhocracy.frontend.ws_url')
    else:
        public_ws_url = _build_ws_url(request, internal_ws_url)
    config['ws_url'] = public_ws_url
    config['pkg_path'] = settings.get('adhocracy.frontend.pkg_path',
                                      '/static/js/Packages')
    config['root_path'] = '/' + settings.get('adhocracy.platform_id',
                                             'adhocracy')
    return config


def root_view(request):
    """Return the embeddee HTML."""
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'static', 'root.html')
    return FileResponse(path, request=request)


def _build_ws_url(request: Request, url: str) -> str:
    url_parsed = urlparse(url)
    ws_domain = request.domain
    ws_port = url_parsed.port or '80'
    ws_scheme = 'wss' if url_parsed.scheme == 'https' else 'ws'
    return '{}://{}:{}'.format(ws_scheme, ws_domain, ws_port)


def includeme(config):
    """Add routing and static view to deliver the frontend application."""
    config.add_static_view('static', 'adhocracy.frontend:static',
                           cache_max_age=0)
    config.add_route('config_json', 'config.json')
    config.add_view(config_view, route_name='config_json', renderer='json',
                    http_cache=0)
    add_frontend_route(config, 'embed', 'embed/{directive}')
    add_frontend_route(config, 'register', 'register')
    add_frontend_route(config, 'login', 'login')
    add_frontend_route(config, 'root', '')


def add_frontend_route(config, name, pattern):
    """Add view and route to adhocracy frontend."""
    config.add_route(name, pattern)
    config.add_view(root_view, route_name=name, renderer='html', http_cache=0)


def main(global_config, **settings):
    """ Return a Pyramid WSGI application to serve the frontend application."""
    config = Configurator(settings=settings)
    includeme(config)
    return config.make_wsgi_app()
