"""Subscriber to notify the websocket server about changed resources."""
from pyramid.threadlocal import get_current_registry

from adhocracy.interfaces import IResourceCreatedAndAdded
from adhocracy.interfaces import IResourceSheetModified
from adhocracy.websockets.client import get_ws_client


def resource_created_and_added_subscriber(event):
    """Send message to websocket server about the new resource."""
    registry = get_current_registry(event.object)
    ws_client = get_ws_client(registry)
    if ws_client is not None:
        resource = event.object
        ws_client.add_message_resource_created(resource)


def resource_modified_subscriber(event):
    """Send message to websocket server about the modified resource."""
    registry = get_current_registry(event.object)
    ws_client = get_ws_client(registry)
    if ws_client is not None:
        resource = event.object
        ws_client.add_message_resource_modified(resource)


def includeme(config):
    """Add subscribers to notify the websocket server about changed data."""
    config.add_subscriber(resource_created_and_added_subscriber,
                          IResourceCreatedAndAdded)
    config.add_subscriber(resource_modified_subscriber,
                          IResourceSheetModified)
