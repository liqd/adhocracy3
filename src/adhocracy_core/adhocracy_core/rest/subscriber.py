"""Subscriber to modify the http response object."""
from pyramid.interfaces import IRequest
from pyramid.events import NewResponse
from adhocracy_core.authentication import AnonymizeHeader
from adhocracy_core.authentication import UserPasswordHeader
from adhocracy_core.interfaces import API_ROUTE_NAME


def set_response_headers(event: NewResponse):
    """Add CORS headers to response for api requests and /."""
    if _is_api_request(event.request) or _is_root_request(event.request):
        add_cors_headers(event)
    else:
        _set_frame_options_header(event)


def add_cors_headers(event: NewResponse):
    """Add CORS headers to response."""
    origin = event.request.headers.get('Origin', '*')
    event.response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, '
                                        'X-User-Path, X-User-Token, '
                                        + AnonymizeHeader + ', '
                                        + UserPasswordHeader,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
    })


def _set_frame_options_header(event: NewResponse):
    event.response.headers.update({'X-Frame-Options': 'DENY'})


def _is_api_request(request: IRequest) -> bool:
    route_name = getattr(request.matched_route, 'name', '')
    return route_name == API_ROUTE_NAME


def _is_root_request(request: IRequest) -> bool:
    return request.path == '/'


def includeme(config):
    """Register response subscriber."""
    config.add_subscriber(set_response_headers, NewResponse)
