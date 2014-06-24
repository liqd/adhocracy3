"""Start Websocket server as main application."""
from configparser import ConfigParser
from logging.config import fileConfig
from os import path
import logging
import os
import sys

from autobahn.asyncio.websocket import WebSocketServerFactory
from ZODB import DB
from adhocracy.websockets.server import ClientCommunicator
from zodburi import resolve_uri
import asyncio


# FIXME make the port configurable
PORT = 8080
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
    if len(args) != 1:
        raise ValueError('Expected 1 command-line argument (the config file), '
                         'but got {}'.format(len(args)))
    config_file = args[0]
    fileConfig(config_file)
    config = _read_config(config_file)
    _check_and_write_pid_file()
    _start_loop(config)


def _check_and_write_pid_file():
    if os.path.isfile(PID_FILE):
        raise RuntimeError('Pidfile already exists: ' + PID_FILE)
    pid = os.getpid()
    pidfile = open(PID_FILE, 'w')
    pidfile.write('%s\n' % pid)
    pidfile.close


def _start_loop(config: ConfigParser):
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


def _remove_pid_file():
    if os.path.isfile(PID_FILE):
        os.unlink(PID_FILE)


def _run_loop_until_interrupted(loop, server):
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.debug('Exiting due to keyboard interrupt (Ctrl-C)')
    finally:
        server.close()
        loop.close()
        return 0


def _read_config(config_file: str) -> ConfigParser:
    config = ConfigParser()
    config.read(config_file)
    _inject_here_variable(config, config_file)
    return config


def _get_zodb_connection(config: ConfigParser) -> dict:
    zodb_uri = config['app:main']['zodbconn.uri']
    logging.debug('Opening ZEO database on {}'.format(zodb_uri))
    storage_factory, dbkw = resolve_uri(zodb_uri)
    storage = storage_factory()
    db = DB(storage, **dbkw)
    return db.open()


def _inject_here_variable(config: ConfigParser, config_file: str):
    """Inject the %(here) variable into a config."""
    dir_containing_config_file = path.dirname(config_file)
    config['app:main']['here'] = dir_containing_config_file
