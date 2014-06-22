"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from configparser import ConfigParser
import os
import subprocess

from pyramid.config import Configurator
from pyramid import testing
from webtest.http import StopableWSGIServer
import pytest
import time

from adhocracy import root_factory


@pytest.fixture()
def dummy_config(request):
    """Return pyramid dummy config."""
    config = testing.setUp()

    def fin():
        testing.tearDown()

    request.addfinalizer(fin)
    return config


@pytest.fixture(scope='class')
def config(request) -> Configurator:
    """Return the adhocracy configuration."""
    config_parser = ConfigParser()
    config_file = request.config.getvalue('pyramid_config')
    config_parser.read(config_file)
    settings = {}
    for option, value in config_parser.items('app:main'):
        settings[option] = value
    configuration = Configurator(settings=settings, root_factory=root_factory)
    return configuration


@pytest.fixture(scope='class')
def zeo(request) -> bool:
    """Start the test zeo server."""
    is_running = os.path.isfile('var/test_zeodata/ZEO.pid')
    if is_running:
        return True
    process = subprocess.Popen('bin/runzeo -Cetc/test_zeo.conf', shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(2)

    def fin():
        print('teardown zeo server')
        process.kill()
        _kill_pid_in_file('var/test_zeodata/ZEO.pid')
        subprocess.call(['rm', '-f', 'var/test_zeodata/Data.fs'])
        subprocess.call(['rm', '-f', 'var/test_zeodata/Data.fs.index'])
        subprocess.call(['rm', '-f', 'var/test_zeodata/Data.fs.lock'])
        subprocess.call(['rm', '-f', 'var/test_zeodata/Data.fs.tmp'])

    request.addfinalizer(fin)
    return True


@pytest.fixture(scope='class')
def websocket(request, zeo) -> bool:
    """Start websocket server."""
    is_running = os.path.isfile('var/WS_SERVER.pid')
    if is_running:
        return True
    config_file = request.config.getvalue('pyramid_config')
    process = subprocess.Popen('bin/start_ws_server ' + config_file,
                               shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(2)

    def fin():
        print('teardown zeo server')
        process.kill()
        _kill_pid_in_file('var/WS_SERVER.pid')

    request.addfinalizer(fin)
    return True


def _kill_pid_in_file(path_to_pid_file):
    if os.path.isfile(path_to_pid_file):
        pid = open(path_to_pid_file).read().strip()
        pid_int = int(pid)
        os.kill(pid_int, 15)
        time.sleep(1)
        # FIXME start_ws_server does not remove the pid file properly
        if os.path.isfile(path_to_pid_file):
            subprocess.call(['rm', path_to_pid_file])


@pytest.fixture(scope='class')
def app(zeo, config, websocket):
    """Return the adhocracy wsgi application."""
    from adhocracy import includeme
    includeme(config)
    return config.make_wsgi_app()


@pytest.fixture(scope='class')
def server(request, app) -> StopableWSGIServer:
    """Return a http server with the adhocracy wsgi application."""
    server = StopableWSGIServer.create(app)

    def fin():
        print('teardown adhocracy http server')
        server.shutdown()

    request.addfinalizer(fin)
    return server
