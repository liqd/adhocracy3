"""Our own Websocket client that notifies the server of changes."""
from threading import Thread
import json
import logging
import time

from pyramid.location import lineage
from websocket import ABNF
from websocket import create_connection
from websocket import WebSocketException
from websocket import WebSocketConnectionClosedException
from websocket import WebSocketTimeoutException

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.utils import exception_to_str
from adhocracy_core.websockets.schemas import ServerNotification
from adhocracy_core.utils import find_graph


logger = logging.getLogger(__name__)


class Client:

    """Websocket Client."""

    def __init__(self, ws_url):
        """Create instance with running thread that talks to the server.

        :param ws_url: the URL of the websocket server to connect to;
               if None, no connection will be set up (useful for testing)
        """
        self.changelog_metadata_messages_to_send = set()
        """Set with :class:`adhocracy_core.resources.subscriber.ChangelogMetadata`
        that will be send to the websocket server with
        :func:`Client.send_messages`."""
        self._ws_url = ws_url
        self._ws_connection = None
        self._is_running = False
        self._is_stopped = False
        if ws_url is not None:
            self._init_listener_thread()

    def _init_listener_thread(self):
        """Init thread that keeps the connection alive."""
        runner = Thread(target=self._run)
        runner.daemon = True
        runner.start()
        self._wait_a_bit_until_connected()

    def _run(self):
        """Start and keep alive connection to the websocket server."""
        assert self._ws_url
        while not self._is_stopped:
            try:
                self._connect_and_receive_and_log_messages()
            except (WebSocketConnectionClosedException, ConnectionError,
                    OSError) as err:
                logger.warning('Problem connecting to Websocket server: %s',
                               exception_to_str(err))
                self._is_running = False
                time.sleep(1)
            except WebSocketException as err:  # pragma: no cover
                logger.warning(
                    'Problem communicating with Websocket server: %s',
                    exception_to_str(err))
                time.sleep(1)

    def _wait_a_bit_until_connected(self):
        """Wait until the connection has been set up, but at most 2.5 secs."""
        for i in range(25):  # pragma: no branch
            if self._is_running:
                break
            time.sleep(.1)

    def _connect_and_receive_and_log_messages(self):
        self._connect_to_server()
        frame = self._ws_connection.recv_frame()
        self._process_frame(frame)

    def _connect_to_server(self):
        if not self._is_connected():
            logger.debug('Try connecting to the Websocket server at '
                         + self._ws_url)
            self._ws_connection = create_connection(self._ws_url)
            self._is_running = True
            logger.debug('Connected to the Websocket server')

    def _is_connected(self):
        return (self._ws_connection is not None and
                self._ws_connection.connected)

    def _process_frame(self, frame: ABNF):
        if not frame:
            logger.warning('Received invalid frame from Websocket server: %s',
                           frame)
        elif frame.opcode == ABNF.OPCODE_TEXT:
            logger.debug('Received text message from Websocket server: %s',
                         frame.data)
        elif frame.opcode == ABNF.OPCODE_CLOSE:
            self._close_connection(b'server triggered close')
            logger.error('Websocket server closed the connection!')
        elif frame.opcode == ABNF.OPCODE_PING:
            self._ws_connection.pong('Hi!')
        else:
            logger.warning('Received unexpected frame from Websocket server: '
                           'opcode=%s, data="%s"', frame.opcode, frame.data)

    def _close_connection(self, reason: bytes):
            self._ws_connection.send_close(reason=reason)
            self._ws_connection.close()
            self._is_running = False

    def send_messages(self, changelog_metadata=[]):
        """Send all changelog messages to the websocket server.

        :param changelog_metadata: list of :class:'ChangelogMetadata',
                                   metadata.resource == None is ignored.

        All websocket exceptions are catched, hoping the problems
        will be solved when you run this method again.
        """
        if not self._is_running:
            return
        try:
            self._send_messages(changelog_metadata)
        except WebSocketTimeoutException:  # pragma: no cover
            logger.warning('Could not send message, connection timeout,'
                           ' try again later')
        except OSError:  # pragma: no cover
            logger.warning('Could not send message, connection is broken,'
                           ' try again later')

    def _send_messages(self, changelog_metadata: list):
        self.changelog_metadata_messages_to_send.update(changelog_metadata)
        created_or_removed_resources = set()
        processed_resources = set()
        while self.changelog_metadata_messages_to_send:
            meta = self.changelog_metadata_messages_to_send.pop()
            # FIXME: if an exception is raised, the current changelog is lost.
            if meta.resource is None:
                continue
            elif meta.created or meta.visibility is VisibilityChange.revealed:
                self._send_resource_event(meta.resource, 'created')
                created_or_removed_resources.add(meta.resource)
                processed_resources.add(meta.resource)
            elif meta.visibility is VisibilityChange.concealed:
                self._send_resource_event(meta.resource, 'removed')
                created_or_removed_resources.add(meta.resource)
                processed_resources.add(meta.resource)
            elif meta.modified:
                self._send_resource_event(meta.resource, 'modified')
                processed_resources.add(meta.resource)
        if processed_resources:
            self._send_modified_messages_for_backrefs(processed_resources)
            self._send_changed_descendant_messages(processed_resources)

    def _send_resource_event(self, resource: IResource, event_type: str):
        schema = ServerNotification().bind(context=resource)
        message = schema.serialize({'event': event_type, 'resource': resource})
        message_text = json.dumps(message)
        logger.debug('Sending message to Websocket server: %s', message_text)
        self._ws_connection.send(message_text)

    def _send_modified_messages_for_backrefs(self, processed_resources: set):
        """
        Send 'modified' messages based on backreferences.

        If a resource has a backreferences pointing to a newly created or
        removed resource, it has been modified from the viewpoint of the
        frontend (since that backreference didn't exist before or now is no
        longer shown).
        """
        random_resource = next(iter(processed_resources))
        graph = find_graph(random_resource)
        if graph is None:  # pragma: no cover
            logger.warning('No graph found--cannot send modified messages for '
                           'backreferencing resources')
            return
        backreferencing_resources = set()
        for resource in processed_resources:
            backreferencing_sheets = graph.get_back_reference_sources(resource)
            for sheet in backreferencing_sheets:
                backreferencing_resources.add(sheet.context)
        for resource in backreferencing_resources:
            if resource not in processed_resources:
                self._send_resource_event(resource, 'modified')

    def _send_changed_descendant_messages(self, processed_resources: set):
        affected_ancestors = set()
        for resource in processed_resources:
            self._add_ancestors(resource, affected_ancestors)
        while affected_ancestors:
            ancestor = affected_ancestors.pop()
            self._send_resource_event(ancestor, 'changed_descendant')

    def _collect_ancestors(self, resource: IResource, affected_ancestors: set):
        ancestors = lineage(resource)
        next(ancestors)  # skip the resource itself
        for ancestor in ancestors:
            if ancestor in affected_ancestors:
                break  # no need to add ancestors twice
            else:
                affected_ancestors.add(ancestor)

    def stop(self):
        self._is_stopped = True
        try:
            if self._is_connected():
                self._close_connection(b'done')
                logger.debug('Websocket client closed')
        except WebSocketException as err:  # pragma: no cover
            logger.warning('Error closing connection to Websocket server: %s',
                           exception_to_str(err))


def get_ws_client(registry) -> Client:
    """Return websocket client object or None."""
    if registry is not None:
        return getattr(registry, 'ws_client', None)


def send_messages_after_commit_hook(success, registry):
    """Send transaction changelog messages to the websocket client."""
    ws_client = get_ws_client(registry)
    if success and ws_client is not None:
        changelog_metadata = registry._transaction_changelog.values()
        ws_client.send_messages(changelog_metadata)


def includeme(config):
    """Add websocket client (`ws_client`) to the registry.

    You need to set the ws server url in your settings to make this work::

        adhocracy.ws_url =  ws://localhost:8080

    """
    settings = config.registry.settings
    ws_url = settings.get('adhocracy.ws_url', '')
    if ws_url:
        ws_client = Client(ws_url=ws_url)
        config.registry.ws_client = ws_client
