"""Subscriber to modify the http response object."""
from pyramid.events import NewResponse


def add_cors_headers(event):
    """Add CORS headers to response."""
    event.response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers':
        'Origin, Content-Type, Accept, X-User-Path, X-User-Token',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
    })


def includeme(config):
    """Register response subscriber."""
    config.add_subscriber(add_cors_headers, NewResponse)
