"""Subscriber to modify the http response object."""
from pyramid.interfaces import IRequest
from pyramid.interfaces import IResponse
from pyramid.events import NewResponse


def add_cors_headers(event):
    """Add CORS headers to response for api requests."""
    if _is_api_request(event.request):
        _set_cors_header(event.request, event.response)
    else:
        _set_frame_options_header(event.response)


def _set_cors_header(request: IRequest, response: IResponse):
    origin = request.headers.get('Origin', '*')
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, '
                                        'X-User-Path, X-User-Token',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
    })


def _set_frame_options_header(response: IResponse):
    response.headers.update({'X-Frame-Options': 'DENY'})


def _is_api_request(request: IRequest) -> bool:
    # assuming api requests have no route
    route_name = getattr(request.matched_route, 'name', None)
    return route_name is None


def includeme(config):
    """Register response subscriber."""
    config.add_subscriber(add_cors_headers, NewResponse)
