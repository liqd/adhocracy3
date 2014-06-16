"""Our own Websocket client that notifies the server of changes."""
from json import dumps
import logging

from adhocracy.interfaces import IResource
from adhocracy.websockets.schemas import Notification


logger = logging.getLogger(__name__)


# TODO create connection to server


def notify_ws_server_of_created_resource(resource: IResource) -> None:
    """Notify the WS server of a newly created resource.

    :param resource: the new resource
    """
    schema = Notification().bind(context=resource)
    _send_json_message(schema.serialize({'event': 'created',
                                         'resource': resource}))


def _send_json_message(json_message: dict) -> None:
    """Send a JSON object as message to the server."""
    text = dumps(json_message)
    logger.debug('Sending message to Websocket server', text)
    # TODO call text.encode() and send
