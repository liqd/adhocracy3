"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from unittest.mock import Mock
from configparser import ConfigParser
import json
import os
import subprocess
import time

from cornice.util import extract_json_data
from cornice.errors import Errors
from pyramid.config import Configurator
from pyramid import testing
from pyramid.traversal import resource_path_tuple
from pytest import fixture
from substanced.objectmap import ObjectMap
from substanced.objectmap import find_objectmap
from webtest.http import StopableWSGIServer
import colander

from adhocracy.interfaces import SheetMetadata, ChangelogMetadata
from adhocracy.interfaces import ResourceMetadata


#####################################
# Integration/Function test helper  #
#####################################

class DummyPool(testing.DummyResource):

    """Dummy Pool based on :class:`pyramid.testing.DummyResource`."""

    def add(self, name, resource, **kwargs):
        self[name] = resource
        resource.__parent__ = self
        resource.__name__ = name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'

    def add_service(self, name, resource, **kwargs):
        resource.__is_service__ = True
        self.add(name, resource)


class DummyPoolWithObjectMap(DummyPool):

    def add(self, name, obj, **kwargs):
        super().add(name, obj)
        objectmap = find_objectmap(self)
        obj.__oid__ = objectmap.new_objectid()
        path_tuple = resource_path_tuple(obj)
        objectmap.add(obj, path_tuple)

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000' + str(hash(obj))


def create_pool_with_graph() -> testing.DummyResource:
    """Return pool like dummy object with objectmap and graph."""
    from adhocracy.interfaces import IPool
    from adhocracy.graph import Graph
    context = DummyPoolWithObjectMap(__oid__=0,
                                     __provides__=IPool)
    objectmap = ObjectMap(context)
    context.__objectmap__ = objectmap
    context.__graph__ = Graph(context)
    return context


##################
# Fixtures       #
##################

@fixture
def resource_meta() -> ResourceMetadata:
    """ Return basic resource metadata."""
    from adhocracy.interfaces import resource_metadata
    from adhocracy.interfaces import IResource
    return resource_metadata._replace(iresource=IResource)


@fixture
def sheet_meta() -> SheetMetadata:
    """ Return basic sheet metadata."""
    from adhocracy.interfaces import sheet_metadata
    from adhocracy.interfaces import ISheet
    return sheet_metadata._replace(isheet=ISheet,
                                   schema_class=colander.MappingSchema)


class CorniceDummyRequest(testing.DummyRequest):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validated = {}
        self.errors = Errors(self)
        self.content_type = 'application/json'
        deserializer = {'application/json': extract_json_data}
        self.registry.cornice_deserializers = deserializer

    def authenticated_userid(self):
        return None

    @property
    def json_body(self):
        return json.loads(self.body)


@fixture
def cornice_request():
    """ Return dummy request with additional validation attributes.

    Additional Attributes:
        `errors`, `validated`, `content_type`
    """
    return CorniceDummyRequest()


@fixture
def changelog_meta() -> ChangelogMetadata:
    """ Return changelog metadata."""
    from adhocracy.resources.subscriber import changelog_metadata
    return changelog_metadata


@fixture
def context() -> testing.DummyResource:
    """ Return dummy context with IResource interface."""
    from adhocracy.interfaces import IResource
    return testing.DummyResource(__provides__=IResource)


@fixture
def pool() -> DummyPool:
    """ Return dummy pool with IPool interface."""
    from adhocracy.interfaces import IPool
    return DummyPool(__provides__=IPool)


@fixture
def item() -> DummyPool:
    """ Return dummy pool with IItem and IMetadata interface."""
    from adhocracy.interfaces import IItem
    from adhocracy.sheets.metadata import IMetadata
    return DummyPool(__provides__=(IItem, IMetadata))


@fixture
def node() -> colander.MappingSchema:
    """Return dummy node."""
    return colander.MappingSchema()


@fixture
def transaction_changelog(changelog_meta):
    """Return transaction_changelog dictionary."""
    from collections import defaultdict
    metadata = lambda: changelog_meta
    return defaultdict(metadata)


@fixture
def mock_sheet() -> Mock:
    """Mock :class:`adhocracy.sheets.GenericResourceSheet`."""
    from adhocracy.interfaces import sheet_metadata
    from adhocracy.interfaces import ISheet
    # FIXME: Use spec=GenericResourceSheet for Mock; however this fails if the
    # mock object is deepcopied.
    sheet = Mock()
    sheet.meta = sheet_metadata._replace(isheet=ISheet)
    return sheet


@fixture
def mock_graph() -> Mock:
    """Mock :class:`adhocracy.graph.Graph`."""
    from adhocracy.graph import Graph
    mock = Mock(spec=Graph)
    return mock


@fixture
def mock_objectmap() -> Mock:
    """Mock :class:`substanced.objectmap.ObjectMap`."""
    from substanced.objectmap import ObjectMap
    mock = Mock(spec=ObjectMap)
    mock.get_reftypes.return_value = []
    return mock


@fixture
def mock_resource_registry() -> Mock:
    """Mock :class:`adhocracy.registry.ResourceContentRegistry`."""
    from adhocracy.registry import ResourceContentRegistry
    mock = Mock(spec=ResourceContentRegistry)
    mock.sheets_meta = {}
    mock.resources_meta = {}
    mock.resource_sheets.return_value = {}
    mock.resource_addables.return_value = {}
    return mock


@fixture
def config(request) -> Configurator:
    """Return dummy testing configuration."""
    config = testing.setUp()
    request.addfinalizer(testing.tearDown)
    return config


@fixture
def registry(config) -> object:
    """Return dummy registry."""
    return config.registry


@fixture
def mock_user_locator(registry) -> Mock:
    """Mock :class:`adhocracy.resource.principal.UserLocatorAdapter`."""
    from zope.interface import Interface
    from substanced.interfaces import IUserLocator
    from adhocracy.resources.principal import UserLocatorAdapter
    locator = Mock(spec=UserLocatorAdapter)
    registry.registerAdapter(lambda y, x: locator, (Interface, Interface),
                             IUserLocator)
    return locator


def _get_settings(request, part, config_path_key='pyramid_config'):
    """Return settings of a config part."""
    config_parser = ConfigParser()
    config_file = request.config.getvalue(config_path_key)
    config_parser.read(config_file)
    settings = {}
    for option, value in config_parser.items(part):
        settings[option] = value
    return settings


@fixture(scope='session')
def settings(request) -> dict:
    """Return app:main and server:main settings."""
    settings = {}
    app = _get_settings(request, 'app:main')
    settings.update(app)
    server = _get_settings(request, 'server:main')
    settings.update(server)
    return settings


@fixture(scope='session')
def ws_settings(request) -> Configurator:
    """Return websocket server settings."""
    return _get_settings(request, 'websockets')


@fixture(scope='class')
def zeo(request) -> bool:
    """Start the test zeo server."""
    pid_file = 'var/test_zeodata/ZEO.pid'
    if _is_running(pid_file):
        return True
    process = subprocess.Popen('bin/runzeo -Cetc/test_zeo.conf', shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(1)

    def fin():
        print('teardown zeo server')
        process.kill()
        _kill_pid_in_file(pid_file)

    request.addfinalizer(fin)
    return True


@fixture(scope='class')
def websocket(request, zeo, ws_settings) -> bool:
    """Start websocket server."""
    pid_file = ws_settings['pid_file']
    if _is_running(pid_file):
        return True
    config_file = request.config.getvalue('pyramid_config')
    process = subprocess.Popen('bin/start_ws_server ' + config_file,
                               shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(1)

    def fin():
        print('teardown websocket server')
        process.kill()
        _kill_pid_in_file(pid_file)

    request.addfinalizer(fin)
    return True


def _kill_pid_in_file(path_to_pid_file):
    if os.path.isfile(path_to_pid_file):
        pid = open(path_to_pid_file).read().strip()
        pid_int = int(pid)
        os.kill(pid_int, 15)
        time.sleep(1)
        subprocess.call(['rm', path_to_pid_file])


def _is_running(path_to_pid_file) -> bool:
    if os.path.isfile(path_to_pid_file):
        pid = open(path_to_pid_file).read().strip()
        pid_int = int(pid)
        try:
            os.kill(pid_int, 0)
        except OSError:
            subprocess.call(['rm', path_to_pid_file])
        else:
            return True


@fixture(scope='class')
def app(zeo, settings, websocket):
    """Return the adhocracy wsgi application."""
    import adhocracy
    configurator = Configurator(settings=settings,
                                root_factory=adhocracy.root_factory)
    configurator.include(adhocracy)
    app = configurator.make_wsgi_app()
    return app


@fixture(scope='class')
def backend(request, settings, app):
    """Return a http server with the adhocracy wsgi application."""
    port = settings['port']
    backend = StopableWSGIServer.create(app, port=port)
    request.addfinalizer(backend.shutdown)
    return backend
