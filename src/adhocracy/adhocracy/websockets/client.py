"""Our own Websocket client that notifies the server of changes."""
from threading import Thread
import json
import logging
import time

from websocket import ABNF
from websocket import create_connection
from websocket import WebSocketException
from websocket import WebSocketConnectionClosedException
from websocket import WebSocketTimeoutException

from pyramid.interfaces import ILocation
from adhocracy.websockets.schemas import Notification


logger = logging.getLogger(__name__)


class Client:

    """Websocket Client.

    Use the `create` class method to get an instance with running
    connection thread.
    """

    is_running = False
    is_stopped = False
    runner = None  # The thread that keeps alive the ws connection
    _ws_url = None
    _ws_connection = None
    _messages_to_send = None

    def __init__(self, ws_url=None):
        self._ws_url = ws_url
        self._messages_to_send = set()

    @classmethod
    def create(cls, ws_url=None):
        """Get instance with running thread that talks to the server."""
        client = cls(ws_url)
        client.runner = Thread(target=client.run)
        client.runner.daemon = True
        client.runner.start()
        time.sleep(2)  # give the websocket client time to connect
        return client

    def run(self):
        """Start and keep alive connection to the websocket server."""
        if not self._ws_url:  # FIXME do we really want this behavior?
            return None
        while not self.is_stopped:
            try:
                self.is_running = True
                self._connect_and_receive_and_log_messages()
            except (WebSocketConnectionClosedException, ConnectionError,
                    OSError):
                logger.exception('Error connecting to the websocket server')
                self.is_running = False
                time.sleep(2)
                continue
            except WebSocketException:
                logger.exception('Error communicating with websocket server')
                time.sleep(2)
                continue

    def _connect_and_receive_and_log_messages(self):
        self._connect_to_server()
        frame = self._ws_connection.recv_frame()
        self._process_frame(frame)

    def _connect_to_server(self):
        if self._ws_connection is None or not self._ws_connection.connected:
            logger.debug('Try connecting to the Websocket server at '
                         + self._ws_url)
            self._ws_connection = create_connection(self._ws_url)
            self.is_connected = True
            logger.debug('Connected to the Websocket server')

    def _process_frame(self, frame: ABNF):
        if not frame:
            logger.warning('Received invalid frame from Websocket server: %s',
                           frame)
        elif frame.opcode == ABNF.OPCODE_TEXT:
            logger.debug('Received text message from Websocket server: %s',
                         frame.data)
        elif frame.opcode == ABNF.OPCODE_CLOSE:
            self._ws_connection.send_close()
            logger.error('Websocket server closed the connection!')
        elif frame.opcode == ABNF.OPCODE_PING:
            self._ws_connection.pong('Hi!')
        else:
            logger.warning('Received unexpected frame from Websocket server: '
                           'opcode=%s, data="%s"', frame.opcode, frame.data)

    def send_messages(self):
        """Send all added messages to the server.

        All websocket exceptions are catched, hoping the problems
        will be solved when you run this method again.

        """
        if not self.is_running:
            return None
        try:
            self._send_messages()
        except WebSocketTimeoutException:
            logger.warning('Counld not send message, connection timeout,'
                           ' try again later')
        except OSError:
            logger.warning('Could not send message, connection is broken,'
                           ' try again later')

    def _send_messages(self):
        for message in self._messages_to_send:
            logger.debug('Try sending message to Websocket server: %s',
                         message)
            self._ws_connection.send(message)
            logger.debug('Send message to the websocket server')
        # FIXME if an exception is raised, messages are send twice, thats bad.
        self._messages_to_send.clear()

    def add_message_resource_created(self, resource: ILocation):
        """Notify the WS server of a newly created resource."""
        schema = Notification().bind(context=resource)
        message = schema.serialize({'event': 'created', 'resource': resource})
        self._messages_to_send.add(json.dumps(message))

    def add_message_resource_modified(self, resource: ILocation):
        """Notify the WS server of a modified resource."""
        schema = Notification().bind(context=resource)
        message = schema.serialize({'event': 'modified', 'resource': resource})
        self._messages_to_send.add(json.dumps(message))

    def stop(self):
        try:
            self._ws_connection.close()
            logger.debug('Websocket client closed')
        except WebSocketException:
            logger.exception('Error closing connection to Websocket server')
        self.is_running = False


def get_ws_client(registry) -> Client:
    """Return websocket client object or None."""
    return getattr(registry, 'ws_client', None)


def send_messages_after_commit_hook(success, registry):
    """Commit hook that gets the websocket client and sends all messages."""
    ws_client = get_ws_client(registry)
    if success and ws_client is not None:
        ws_client.send_messages()


def includeme(config):
    """Add websocket client (`ws_client`) to the registry.

    You need to set the ws server url in your settings to make this work::

        adhocracy.ws_url =  ws://localhost:8080

    """
    settings = config.registry.settings
    ws_url = settings.get('adhocracy.ws_url', '')
    if ws_url:
        ws_client = Client.create(ws_url=ws_url)
        config.registry.ws_client = ws_client
