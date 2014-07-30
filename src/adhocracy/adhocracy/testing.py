"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from unittest.mock import Mock
from configparser import ConfigParser
import copy
import json
import os
import subprocess
import time

from pyramid.config import Configurator
from pyramid import testing
from pyramid.traversal import resource_path_tuple
from substanced.objectmap import ObjectMap
from substanced.objectmap import find_objectmap
from splinter import Browser
from webtest.http import StopableWSGIServer
from pytest_splinter.plugin import Browser as PytestSplinterBrowser
from pytest_splinter.plugin import patch_webdriver
from pytest_splinter.plugin import patch_webdriverelement
from pytest import fixture
import colander

from adhocracy import root_factory
from adhocracy.interfaces import SheetMetadata
from adhocracy.interfaces import ResourceMetadata


#####################################
# Integration/Function test helper  #
#####################################


class DummyPoolWithObjectMap(testing.DummyResource):

    def add(self, name, obj, **kwargs):
        self[name] = obj
        obj.__name__ = name
        obj.__parent__ = self
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

@fixture()
def resource_meta() -> ResourceMetadata:
    """ Return basic resource metadata."""
    from adhocracy.interfaces import resource_metadata
    from adhocracy.interfaces import IResource
    return resource_metadata._replace(iresource=IResource)


@fixture()
def sheet_meta() -> SheetMetadata:
    """ Return basic sheet metadata."""
    from adhocracy.interfaces import sheet_metadata
    from adhocracy.interfaces import ISheet
    return sheet_metadata._replace(isheet=ISheet,
                                   schema_class=colander.MappingSchema)


@fixture()
def context() -> testing.DummyResource:
    """ Return dummy context with IResource interface."""
    from adhocracy.interfaces import IResource
    return testing.DummyResource(__provides__=IResource)


class DummyPool(testing.DummyResource):

    """Dummy Pool based on :class:`pyramid.testing.DummyResource`."""

    def add(self, name, resource, **kwargs):
        self[name] = resource
        resource.__parent__ = self
        resource.__name__ = name

    def next_name(self, obj, prefix=''):
        return prefix + '_0000000'


@fixture()
def pool() -> DummyPool:
    """ Return dummy pool with IPool interface."""
    from adhocracy.interfaces import IPool
    return DummyPool(__provides__=IPool)


@fixture()
def node() -> colander.MappingSchema:
    """Return dummy node."""
    return colander.MappingSchema()


@fixture()
def mock_sheet() -> Mock:
    """Mock :class:`adhocracy.sheets.GenericResourceSheet`."""
    from adhocracy.sheets import GenericResourceSheet
    from adhocracy.interfaces import sheet_metadata
    from adhocracy.interfaces import ISheet
    sheet = Mock(spec=GenericResourceSheet)
    sheet.meta = sheet_metadata._replace(isheet=ISheet)
    return sheet


@fixture()
def mock_graph() -> Mock:
    """Mock :class:`adhocracy.graph.Graph`."""
    from adhocracy.graph import Graph
    mock = Mock(spec=Graph)
    return mock


@fixture()
def mock_objectmap() -> Mock:
    """Mock :class:`substanced.objectmap.ObjectMap`."""
    from substanced.objectmap import ObjectMap
    mock = Mock(spec=ObjectMap)
    mock.get_reftypes.return_value = []
    return mock


@fixture()
def mock_resource_registry() -> Mock:
    """Mock :class:`adhocracy.registry.ResourceContentRegistry`."""
    from adhocracy.registry import ResourceContentRegistry
    mock = Mock(spec=ResourceContentRegistry)
    mock.sheets_metadata.return_value = {}
    mock.resources_metadata.return_value = {}
    mock.resource_sheets.return_value = {}
    mock.resource_addables.return_value = {}
    return mock


@fixture()
def config(request) -> Configurator:
    """Return dummy testing configuration."""
    config = testing.setUp()
    request.addfinalizer(testing.tearDown)
    return config


@fixture()
def registry(config) -> object:
    """Return dummy registry."""
    return config.registry


@fixture()
def mock_user_locator(registry) -> Mock:
    """Mock :class:`adhocracy.resource.principal.UserLocatorAdapter`."""
    from zope.interface import Interface
    from substanced.interfaces import IUserLocator
    from adhocracy.resources.principal import UserLocatorAdapter
    locator = Mock(spec=UserLocatorAdapter)
    registry.registerAdapter(lambda y, x: locator, (Interface, Interface),
                             IUserLocator)
    return locator


@fixture(scope='class')
def configurator(request) -> Configurator:
    """Return the adhocracy configuration.

    The path to the config file is set by the py.test --pc argument.
    """
    config_parser = ConfigParser()
    config_file = request.config.getvalue('pyramid_config')
    config_parser.read(config_file)
    settings = {}
    for option, value in config_parser.items('app:main'):
        settings[option] = value
    configuration = Configurator(settings=settings, root_factory=root_factory)
    return configuration


@fixture(scope='class')
def zeo(request) -> bool:
    """Start the test zeo server."""
    is_running = os.path.isfile('var/test_zeodata/ZEO.pid')
    if is_running:
        return True
    process = subprocess.Popen('bin/runzeo -Cetc/test_zeo.conf', shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(1)

    def fin():
        print('teardown zeo server')
        process.kill()
        _kill_pid_in_file('var/test_zeodata/ZEO.pid')

    request.addfinalizer(fin)
    return True


@fixture(scope='class')
def websocket(request, zeo) -> bool:
    """Start websocket server."""
    is_running = os.path.isfile('var/WS_SERVER.pid')
    if is_running:
        return True
    config_file = request.config.getvalue('pyramid_config')
    process = subprocess.Popen('bin/start_ws_server ' + config_file,
                               shell=True,
                               stderr=subprocess.STDOUT)
    time.sleep(1)

    def fin():
        print('teardown websocket server')
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
        if os.path.isfile(path_to_pid_file):
            subprocess.call(['rm', path_to_pid_file])


@fixture(scope='class')
def app(zeo, configurator, websocket):
    """Return the adhocracy wsgi application."""
    import adhocracy
    configurator.include(adhocracy)
    return configurator.make_wsgi_app()


@fixture(scope='class')
def server(request, app) -> StopableWSGIServer:
    """Return a http server with the adhocracy wsgi application."""
    server = StopableWSGIServer.create(app)

    def fin():
        print('teardown adhocracy http server')
        server.shutdown()

    request.addfinalizer(fin)
    return server


@fixture(scope='session')
def server_static(request) -> StopableWSGIServer:
    """Return a http server that only serves the static files."""
    from adhocracy.frontend import includeme
    config = Configurator(settings={})
    includeme(config)
    app = config.make_wsgi_app()

    server = StopableWSGIServer.create(app)

    def fin():
        print('teardown static http server')
        server.shutdown()

    request.addfinalizer(fin)
    return server


class SplinterBrowser(PytestSplinterBrowser):

    """ Extended Splinter browser."""

    def evaluate_script_with_kwargs(self, code: str, **kwargs) -> object:
        """Replace kwargs in javascript code and evaluate."""
        code_with_kwargs = self.compile_js_code(code, **kwargs)
        return self.evaluate_script(code_with_kwargs)

    def compile_js_code(self, code: str, **kwargs) -> str:
        """Generate a single JavaScript expression from complex code.

        This is accomplished by wrapping the code in a JavaScript function
        and passing any key word arguments to that function.  All arguments
        will be JSON encoded.

        :param code: any JavaScript code
        :param kwargs: arguments that will be passed to the wrapper function

        :returns: a string containing a single JavaScript expression suitable
            for consumption by splinter's ``evaluate_script``

        >>> code = "var a = 1; test.y = a; return test;"
        >>> compile_js_code(code, test={"x": 2})
        '(function(test) {var a = 1; test.y = a; return test;})({"x": 2})'

        """
        # make sure keys and values are in the same order
        keys = []
        values = []
        for key in kwargs:
            keys.append(key)
            values.append(kwargs[key])

        keys = ', '.join(keys)
        values = ', '.join((json.dumps(v) for v in values))

        return '(function({}) {{{}}})({})'.format(keys, code, values)


@fixture(scope='session')
def splinter_browser_load_condition():
    """Custom browser condition fixture to check that html page is fully loaded.

    The splinter browser has no general "wait for page load" function:
    https://github.com/cobrateam/splinter/issues/237

    """
    def is_page_loaded(browser):
        code = 'document.readyState === "complete";'
        return browser.evaluate_script(code)

    return is_page_loaded


@fixture
def browser_instance(request,
                     splinter_selenium_socket_timeout,
                     splinter_selenium_implicit_wait,
                     splinter_selenium_speed,
                     splinter_webdriver,
                     splinter_browser_load_condition,
                     splinter_browser_load_timeout,
                     splinter_file_download_dir,
                     splinter_download_file_types,
                     splinter_firefox_profile_preferences,
                     splinter_driver_kwargs,
                     splinter_window_size,
                     ):
    """Splinter browser wrapper instance.

    Based on: :mod:`pytest_splinter.plugin.browser_instance`

    This fixture can be used to setup the other splinter fixtures:

       https://pypi.python.org/pypi/pytest-splinter

    """
    patch_webdriver(splinter_selenium_socket_timeout)
    patch_webdriverelement()

    kwargs = {}
    if splinter_webdriver == 'firefox':
        kwargs['profile_preferences'] = dict({
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir':
                splinter_file_download_dir,
            'browser.helperApps.neverAsk.saveToDisk':
                splinter_download_file_types,
            'browser.helperApps.alwaysAsk.force': False,
        }, **splinter_firefox_profile_preferences)
    if splinter_driver_kwargs:
        kwargs.update(splinter_driver_kwargs)

    browser = SplinterBrowser(
        splinter_webdriver,
        visit_condition=splinter_browser_load_condition,
        visit_condition_timeout=splinter_browser_load_timeout,
        **copy.deepcopy(kwargs))
    browser.driver.implicitly_wait(splinter_selenium_implicit_wait)
    browser.driver.set_speed(splinter_selenium_speed)
    if splinter_window_size:
        browser.driver.set_window_size(*splinter_window_size)

    return browser


@fixture()
def browser_root(browser_instance, server) -> Browser:
    """browser_instance with url=root.html."""
    url = server.application_url + 'frontend_static/root.html'
    browser_instance.visit(url)

    def angular_app_loaded(browser):
        code = 'window.hasOwnProperty("adhocracy") && window.adhocracy.hasOwnProperty("loadState") && window.adhocracy.loadState === "complete";'  # noqa
        return browser.evaluate_script(code)
    browser_instance.wait_for_condition(angular_app_loaded, 5)

    return browser_instance


@fixture()
def browser_test(browser_instance, server) -> Browser:
    """browser_instance with url=test.html."""
    url = server.application_url + 'frontend_static/test.html'
    browser_instance.visit(url)

    def jasmine_finished(browser):
        code = 'jsApiReporter.finished'
        return browser.evaluate_script(code)
    browser_instance.wait_for_condition(jasmine_finished, 5)

    return browser_instance
