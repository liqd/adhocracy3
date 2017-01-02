"""Start Websocket server as main application."""
from configparser import ConfigParser
from logging.config import fileConfig
from os import path
from signal import signal
from signal import SIGTERM
import yaml
import logging
import os
import sys
import errno

from autobahn.asyncio.websocket import WebSocketServerFactory
from tzf.pyramid_yml import _translate_config_path
from tzf.pyramid_yml import _env_filenames
from ZODB import DB
from adhocracy_core.websockets.server import ClientCommunicator
from zodburi import resolve_uri
import asyncio


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
    port = _read_config_variable_or_die(config, 'port', is_int=True)
    pid_file = _read_config_variable_or_die(config, 'pid_file')
    _check_and_write_pid_file(pid_file)
    _register_sigterm_handler(pid_file)
    _start_loop(config, port, pid_file)


def _read_config_variable_or_die(config: ConfigParser, name: str,
                                 is_int: bool=False):
    """Read a variable from the [websockets] section of `config`.

    :raise RuntimeError: if the variable does not exist or doesn't have the
                         expected type
    """
    result = config.get('websockets', name, fallback=None)
    if not result:
        raise RuntimeError('Config entry "{}" in [websockets] section '
                           'missing or empty'.format(name))
    if is_int:
        try:
            result = int(result)
        except ValueError:
            raise RuntimeError('Config entry "{}" in [websockets] section is '
                               'not an integer: {}'.format(name, result))
    return result


def _check_and_write_pid_file(pid_file: str):
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            old_pid = int(f.read().split('\n')[0])
            try:
                os.kill(old_pid, 0)
            except OSError as exc:
                if exc.errno != errno.ESRCH:
                    raise RuntimeError('Pidfile already exists: ' + pid_file)
    pid = os.getpid()
    with open(pid_file, 'w') as pidfile:
        pidfile.write('%s\n' % pid)


def _register_sigterm_handler(pid_file: str):
    """Register handler for the SIGTERM signal ('kill' command).

    The new handler will remove the PID file and exit.
    """
    def sigterm_handler(sig, frame):
        logger.info('Kill signal (SIGTERM) received, exiting')
        _remove_pid_file(pid_file)
        sys.exit()

    signal(SIGTERM, sigterm_handler)


def _start_loop(config: ConfigParser, port: int, pid_file: str):
    try:
        database = _get_zodb_database(config)
        ClientCommunicator.zodb_database = database
        rest_url = _get_rest_url(config)
        ClientCommunicator.rest_url = rest_url
        factory = WebSocketServerFactory('ws://localhost:{}'.format(port))
        factory.protocol = ClientCommunicator
        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, port=port)
        logger.debug('Started WebSocket server listening on port %i', port)
        server = loop.run_until_complete(coro)
        _run_loop_until_interrupted(loop, server)
    finally:
        logger.info('Stopped WebSocket server')
        _remove_pid_file(pid_file)


def _remove_pid_file(pid_file: str):
    if os.path.isfile(pid_file):
        os.unlink(pid_file)


def _run_loop_until_interrupted(loop, server):
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.debug('Exiting due to keyboard interrupt (Ctrl-C)')
    finally:
        server.close()
        loop.close()
        return 0


def _read_config(config_file: str) -> ConfigParser:
    config = ConfigParser()
    config.read(config_file)
    _inject_here_variable(config, config_file)
    return config


def _get_zodb_database(config: ConfigParser) -> dict:  # pragma: no cover
    config_locations = config['app:main']['yaml.location']
    if not isinstance(config_locations, (list, tuple)):
        config_locations = config_locations.split(',')
    env = config['app:main'].get('env', 'dev')
    file_paths = []
    files = ['config.yaml', 'config.yml']
    for location in config_locations:
        path = _translate_config_path(location)
        current_files = files
        if os.path.isfile(path):
            path, current_files = os.path.split(path)
            current_files = [current_files]
        for config_path in [
            os.path.join(path, f) for f in _env_filenames(current_files, env)
        ]:
            if os.path.isfile(config_path):
                file_paths.append(config_path)
    zodb_uri = ''
    for config_file in file_paths:
        with open(config_file, 'r') as stream:
            yaml_config = yaml.load(stream)
            configurator = yaml_config.get('configurator') or {}
            zodbconn = configurator.get('zodbconn') or {}
            new_zodb_uri = zodbconn.get('uri')
            if new_zodb_uri:
                zodb_uri = new_zodb_uri
    logger.info('Getting ZEO database on {}'.format(zodb_uri))
    storage_factory, dbkw = resolve_uri(zodb_uri)
    storage = storage_factory()
    db = DB(storage, **dbkw)
    return db


def _get_rest_url(config: ConfigParser) -> dict:
    return config['websockets']['rest_url']


def _inject_here_variable(config: ConfigParser, config_file: str):
    """Inject the %(here) variable into a config."""
    dir_containing_config_file = path.dirname(config_file)
    config['app:main']['here'] = dir_containing_config_file
