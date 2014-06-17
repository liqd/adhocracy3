"""Our own Websocket client that notifies the server of changes."""
from json import dumps
from threading import Thread
import logging

from websocket import ABNF
from websocket import create_connection
from websocket import WebSocketException

from adhocracy.interfaces import IResource
from adhocracy.websockets.main import PORT
from adhocracy.websockets.schemas import Notification


ENABLED = True

logger = logging.getLogger(__name__)
ws = None


def disable() -> None:
    """Disable the Websocket client. This can be useful for tests."""
    global ENABLED
    ENABLED = False
    logger.debug('Websocket client disabled')
    if ws:
        _close_connection()


def _close_connection():
    """Close the connection to the Websocket server."""
    global ws
    try:
        ws.close()
        logger.debug('Websocket client closed')
    except WebSocketException:
        logger.exception('Error closing connection to Websocket server')
    ws = None


def _connect_to_server() -> None:
    """Connect to the Websocket server."""
    if ENABLED:
        global ws
        try:
            ws = create_connection('ws://localhost:{}'.format(PORT))
        except (WebSocketException, ConnectionError):
            logger.exception('Error opening connection to Websocket server')
            disable()


def _start_receiving_thread() -> None:
    """Start a daemon thread that receives WS messages in the background."""
    if ENABLED and ws is not None:
        thread = Thread(
            target=_receive_and_log_messages_and_keep_connection_alive)
        thread.daemon = True
        thread.start()


def _receive_and_log_messages_and_keep_connection_alive():
    """Receive messages from the WS server and log them away.

    Also answer to ping messages to keep the connection alive.
    """
    while ENABLED:
        frame = ws.recv_frame()
        _process_frame(frame)


def _process_frame(frame: ABNF) -> None:
    if not frame:
        logger.warning('Received invalid frame from Websocket server: %s',
                       frame)
    elif frame.opcode == ABNF.OPCODE_TEXT:
        logger.debug('Received text message from Websocket server: %s',
                     frame.data)
    elif frame.opcode == ABNF.OPCODE_CLOSE:
        ws.send_close()
        logger.error('Websocket server closed the connection!')
    elif frame.opcode == ABNF.OPCODE_PING:
        ws.pong('Hi!')
    else:
        logger.warning('Received unexpected frame from Websocket server: '
                       'opcode=%s, data="%s"', frame.opcode, frame.data)


def notify_ws_server_of_created_resource(resource: IResource) -> None:
    """Notify the WS server of a newly created resource.

    :param resource: the new resource
    """
    schema = Notification().bind(context=resource)
    _send_json_message(schema.serialize({'event': 'created',
                                         'resource': resource}))


def _send_json_message(json_message: dict) -> None:
    """Send a JSON object as message to the server."""
    if ENABLED:
        text = dumps(json_message)
        logger.debug('Sending message to Websocket server: %s', text)
        try:
            ws.send(text)
        except WebSocketException:
            logger.exception('Error sending message to Websocket server')


def includeme(config):
    """Configure WebSockets client."""
    _connect_to_server()
    _start_receiving_thread()
