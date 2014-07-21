"""Public py.test fixtures: http://pytest.org/latest/fixture.html. """
from configparser import ConfigParser
import copy
import json
import os
import subprocess
import time

from pyramid.config import Configurator
from pyramid import testing
from splinter import Browser
from webtest.http import StopableWSGIServer
from pytest_splinter.plugin import Browser as PytestSplinterBrowser
from pytest_splinter.plugin import patch_webdriver
from pytest_splinter.plugin import patch_webdriverelement
import pytest

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


@pytest.fixture(scope='session')
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


@pytest.fixture(scope='session')
def splinter_browser_load_condition():
    """Custom browser condition fixture to check that html page is fully loaded.

    The splinter browser has no general "wait for page load" function:
    https://github.com/cobrateam/splinter/issues/237

    """
    def is_page_loaded(browser):
        code = 'document.readyState === "complete"';
        return browser.evaluate_script(code)

    return is_page_loaded


@pytest.fixture
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


@pytest.fixture()
def browser_root(browser_instance, server) -> Browser:
    """browser_instance with url=root.html."""
    url = server.application_url + 'frontend_static/root.html'
    browser_instance.visit(url)

    def angularAppLoaded(browser):
        code = 'window.hasOwnProperty("adhocracy") && window.adhocracy.hasOwnProperty("loadState") && window.adhocracy.loadState === "complete";'
        return browser.evaluate_script(code)
    browser_instance.wait_for_condition(angularAppLoaded, 5)

    return browser_instance


@pytest.fixture()
def browser_test(browser_instance, server) -> Browser:
    """browser_instance with url=test.html."""
    url = server.application_url + 'frontend_static/test.html'
    browser_instance.visit(url)

    def jasmineFinished(browser):
        code = 'jsApiReporter.finished'
        return browser.evaluate_script(code)
    browser_instance.wait_for_condition(jasmineFinished, 5)

    return browser_instance
