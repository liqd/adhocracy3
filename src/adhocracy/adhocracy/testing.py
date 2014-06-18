"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from configparser import ConfigParser

from pyramid.config import Configurator
import pytest

from adhocracy import root_factory


@pytest.fixture()
def config(request):
    """Return the adhocracy configuration object."""
    config_parser = ConfigParser()
    config_file = request.config.getvalue('pyramid_config')
    config_parser.read(config_file)
    settings = {}
    for option, value in config_parser.items('app:main'):
        settings[option] = value
    configuration = Configurator(settings=settings, root_factory=root_factory)
    return configuration
