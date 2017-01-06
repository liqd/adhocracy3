"""Frontend view and simple pyramid app configurations."""
import pkg_resources

from pyramid.renderers import render
from pyramid.config import Configurator
from pyramid.events import NewResponse
from pyramid.response import FileResponse
from pyramid.response import Response

from adhocracy_core.rest.subscriber import add_cors_headers


def config_view(request):
    """Return the frontend configuration."""
    settings = request.registry['config']
    config = {}
    config.update(settings.adhocracy.frontend)
    config['canonical_url'] = settings.adhocracy.canonical_url
    config['redirect_url'] = settings.adhocracy.redirect_url
    config['rest_platform_path'] = settings.adhocracy.rest_platform_path
    config['rest_url'] = settings.adhocracy.rest_url
    config['trusted_domains'] = settings.adhocracy.trusted_domains
    config['captcha_enabled'] = settings.adhocracy.captcha_enabled
    config['captcha_url'] = settings.adhocracy.captcha_frontend_url
    config['site_name'] = settings.adhocracy.site_name
    config['service_konto.enabled'] = settings.adhocracy.service_konto.enabled
    config['service_konto.api_url'] = settings.adhocracy.service_konto.api_url
    use_cachbust = settings.configurator.cachebust.enabled
    if not use_cachbust:  # ease testing
        return config
    config['cachebust'] = use_cachbust
    config['cachebust_suffix'] = cachebust_query_params(request)
    return config


def cachebust_query_params(request) -> dict:
    """Return cachebust query params.

    Due to simplicity, we currently use the same query parameter for all
    static resources. If we use individual checksums, this will go away.

    :raises FileNotFoundError: if asset 'build/stylesheets/a3.css' is not
    available.
    """
    url = request.cachebusted_url('adhocracy_frontend:build/'
                                  'stylesheets/a3.css')
    if '?' in url:
        query_params = url.split('?')[1]
    else:
        query_params = None
    return query_params


def require_config_view(request):
    """Return require config."""
    query_params = cachebust_query_params(request)
    config = config_view(request)
    result = render(
        'adhocracy_frontend:build/require-config.js.mako', {
            'url_args': query_params,
            'minify': not config['debug'],
        }, request=request)
    response = Response(result)
    response.content_type = 'application/javascript'
    return response


def root_view(request):
    """Return the embeddee HTML."""
    if not hasattr(request, 'cachebusted_url'):  # ease testing
        return Response()
    css_path = 'stylesheets/a3.css'
    query_params = cachebust_query_params(request)
    result = render(
        'adhocracy_frontend:build/root.html.mako',
        {'css': [request.cachebusted_url('adhocracy_frontend:build/'
                                         'lib/leaflet/dist/leaflet.css'),
                 request.cachebusted_url('adhocracy_frontend:build/'
                                         + css_path),
                 ],
         'js': [request.cachebusted_url('adhocracy_frontend:build/'
                                        'lib/requirejs/require.js'),
                request.cachebusted_url('adhocracy_frontend:build/'
                                        'lib/jquery/dist/jquery.min.js'),
                '/static/require-config.js%s' % (
                    '?' + query_params if query_params else ''),
                ],
         'meta_api': '/static/meta_api.json',
         'config': '/config.json',
         },
        request=request)
    response = Response(result)
    return response


def adhocracy_sdk_view(request):
    """Return AdhocracySDK.js."""
    path = pkg_resources.resource_filename('adhocracy_frontend',
                                           'build/js/AdhocracySDK.js')
    return FileResponse(path, request=request)


def service_konto_finish_view(request):
    """View that passes a service konto token back to adhocracy."""
    path = pkg_resources.resource_filename('adhocracy_frontend',
                                           'build/ServiceKontoFinish.html')
    return FileResponse(path, request=request)


def includeme(config):
    """Add routing and static view to deliver the frontend application."""
    settings = config.registry['config']
    cachebust_enabled = settings.configurator.cachebust.enabled
    if cachebust_enabled:
        cache_max_age = 30 * 24 * 60 * 60  # 30 days
    else:
        cache_max_age = 0
    config.add_route('config_json', 'config.json')
    config.add_view(config_view, route_name='config_json', renderer='json',
                    http_cache=(cache_max_age, {'public': True}))
    add_frontend_route(config, 'embed', 'embed/{directive}')
    add_frontend_route(config, 'register', 'register')
    add_frontend_route(config, 'login', 'login')
    add_frontend_route(config, 'password_reset', 'password_reset/')
    add_frontend_route(config, 'create_password_reset',
                       'create_password_reset')
    add_frontend_route(config, 'activate', 'activate/{key}')
    add_frontend_route(config, 'activation_error', 'activation_error')
    add_frontend_route(config, 'root', '')
    add_frontend_route(config, 'resource', 'r/*path')
    config.add_route('require_config', 'static/require-config.js')
    config.add_view(require_config_view, route_name='require_config',
                    http_cache=(cache_max_age, {'public': True}))
    # AdhocracySDK shall not be cached the way other static files are cached
    config.add_route('adhocracy_sdk', 'AdhocracySDK.js')
    config.add_view(adhocracy_sdk_view, route_name='adhocracy_sdk')
    config.add_route('service_konto_finish', 'service_konto_finish')
    config.add_view(service_konto_finish_view,
                    route_name='service_konto_finish')
    config.add_static_view('static', 'adhocracy_frontend:build/',
                           cache_max_age=cache_max_age)
    config.add_subscriber(add_cors_headers, NewResponse)


def add_frontend_route(config, name, pattern):
    """Add view and route to adhocracy frontend."""
    config.add_route(name, pattern)
    config.add_view(root_view, route_name=name, renderer='html')


def main(global_config, **settings):
    """Return a Pyramid WSGI application to serve the frontend application."""
    config = Configurator(settings=settings)
    config.include('tzf.pyramid_yml')
    includeme(config)
    return config.make_wsgi_app()
