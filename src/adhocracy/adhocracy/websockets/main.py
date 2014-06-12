"""Start Websocket server as main application."""
from configparser import ConfigParser
from os import path
import logging

from autobahn.asyncio.websocket import WebSocketServerFactory
from ZODB import DB
from zodburi import resolve_uri
import asyncio

from adhocracy.websockets import ClientCommunicator


PORT = 8080
LOG_FILE_NAME = 'adhocracy-ws.log'
LOG_LEVEL = logging.DEBUG

logger = logging.getLogger(__name__)


def main(args: list) -> int:
    """Start WebSockets server.

    :param args: the command-line arguments -- we expect just one: the
                 config file to use
    :return: 0 on success
    """
    config = _read_config(args)
    _configure_logger(config)
    app_root = _connect_to_zeo_server_and_return_app_root(config)
    factory = WebSocketServerFactory('ws://localhost:{}'.format(PORT))
    factory.protocol = ClientCommunicator
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', PORT)
    logger.debug('Started WebSocket server listening on port %i', PORT)
    server = loop.run_until_complete(coro)
    _run_loop_until_interrupted(loop, server)


def _run_loop_until_interrupted(loop, server) -> None:
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.debug('Exiting due to keyboard interrupt (Ctrl-C)')
    finally:
        server.close()
        loop.close()
        return 0


def _read_config(args: list) -> ConfigParser:
    if len(args) != 1:
        raise ValueError('Excepted 1 command-line argument (the config file), '
                         'but got {}'.format(len(args)))
    config_file = args[0]
    config = ConfigParser()
    config.read(config_file)
    _inject_here_variable(config, config_file)
    return config


def _configure_logger(config: ConfigParser) -> None:
    fmt = config['formatter_generic'].get('format', raw=True)
    if format is None:
        logging.basicConfig(filename=LOG_FILE_NAME, level=LOG_LEVEL)
    else:
        logging.basicConfig(filename=LOG_FILE_NAME, level=LOG_LEVEL,
                            format=fmt)


def _connect_to_zeo_server_and_return_app_root(config: ConfigParser) -> dict:
    zodb_uri = config['app:main']['zodbconn.uri']
    logging.debug('Opening ZEO database on {}'.format(zodb_uri))
    storage_factory, dbkw = resolve_uri(zodb_uri)
    storage = storage_factory()
    db = DB(storage, **dbkw)
    conn = db.open()
    zodb_root = conn.root()
    return zodb_root['app_root']


def _inject_here_variable(config: ConfigParser, config_file: str) -> None:
    """Inject the %(here) variable into a config."""
    dir_containing_config_file = path.dirname(config_file)
    config['app:main']['here'] = dir_containing_config_file
