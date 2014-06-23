"""Start Websocket server as main application."""
# REVIEW maybe rename this module to scripts.py or start_ws_server.py then its
# more clear what modules is doing.
# REVIEW [joka]: maybe the follwing structure is more readable:
#   client.py server.py start_ws_server.py __init__.py(only for setup stuff)
import os
import sys
from configparser import ConfigParser
from os import path
import logging

from autobahn.asyncio.websocket import WebSocketServerFactory
from ZODB import DB
from zodburi import resolve_uri
import asyncio

from adhocracy.websockets import ClientCommunicator


# FIXME make the port configurable
PORT = 8080
# REVIEW just log to stdout,
# this way other tools can take care for log file creation and logrotaion
LOG_FILE_NAME = 'adhocracy-ws.log'
LOG_LEVEL = logging.DEBUG
# FIXME make pid file path configurable
PID_FILE = 'var/WS_SERVER.pid'

logger = logging.getLogger(__name__)


def main(args=[]) -> int:
    """Start WebSockets server.

    :param args: the command-line arguments -- we expect just one: the
                 config file to use
    :return: 0 on success
    """
    if not args:
        args = sys.argv[1:]
    config = _read_config(args)
    _configure_logger(config)
    _check_and_write_pid_file()
    try:
        connection = _get_zodb_connection(config)
        ClientCommunicator.zodb_connection = connection
        factory = WebSocketServerFactory('ws://localhost:{}'.format(PORT))
        factory.protocol = ClientCommunicator
        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, port=PORT)
        logger.debug('Started WebSocket server listening on port %i', PORT)
        server = loop.run_until_complete(coro)
        _run_loop_until_interrupted(loop, server)
    finally:
        logging.debug('Stopped WebSocket server')
        _remove_pid_file()


def _check_and_write_pid_file():
    if os.path.isfile(PID_FILE):
        raise RuntimeError('Pidfile already exists: ' + PID_FILE)
    pid = os.getpid()
    pidfile = open(PID_FILE, 'w')
    pidfile.write('%s' % pid)
    pidfile.close


def _remove_pid_file():
    if os.path.isfile(PID_FILE):
        os.unlink(PID_FILE)


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


def _get_zodb_connection(config: ConfigParser) -> dict:
    zodb_uri = config['app:main']['zodbconn.uri']
    logging.debug('Opening ZEO database on {}'.format(zodb_uri))
    storage_factory, dbkw = resolve_uri(zodb_uri)
    storage = storage_factory()
    db = DB(storage, **dbkw)
    return db.open()


def _inject_here_variable(config: ConfigParser, config_file: str) -> None:
    """Inject the %(here) variable into a config."""
    dir_containing_config_file = path.dirname(config_file)
    config['app:main']['here'] = dir_containing_config_file
