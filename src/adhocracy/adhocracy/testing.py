"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from configparser import ConfigParser
import os
import subprocess

from pyramid.config import Configurator
import pytest

from adhocracy import root_factory


@pytest.fixture()
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


@pytest.fixture()
def zeo(request) -> bool:
    """Start the test zeo server."""
    subprocess.call(['mkdir', 'var/test_zeodata'])
    process = subprocess.Popen('bin/runzeo -Cetc/test_zeo.conf', shell=True,
                               stderr=subprocess.STDOUT)

    def fin():
        print('teardown zeo server')
        process.kill()
        zeo_pid = open('var/test_zeodata/ZEO.pid').read().strip()
        zeo_pid_int = int(zeo_pid)
        os.kill(zeo_pid_int, 15)
        subprocess.call(['rm', '-fr', 'var/test_zeodata'])

    request.addfinalizer(fin)
    return True
