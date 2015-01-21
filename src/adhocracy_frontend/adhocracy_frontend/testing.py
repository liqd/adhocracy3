"""Public fixtures to work with the test browser and the adhocracy frontend."""
import subprocess
import re
import types
import json
from pytest import fixture
from splinter import Browser
from pytest_splinter.plugin import browser_instance_getter

from adhocracy_core.testing import _get_settings


def pytest_addoption(parser):
    """Add pytest option `frontend_pc`."""
    parser.addoption(
        '--frontend_pc',
        action='store',
        default='etc/frontend_test.ini',
        metavar='path',
        dest='frontend_pyramid_config',
    )


@fixture(scope='session')
def frontend_url(request) -> dict:
    """Return the frontend url."""
    settings = _get_settings(request, 'server:main', 'frontend_pyramid_config')
    host = settings['host']
    port = settings['port']
    url = 'http://{}:{}/'.format(host, port)
    return url


@fixture(scope='session')
def frontend(request, supervisor) -> str:
    """Start the frontend server with supervisor."""
    output = subprocess.check_output(
        'bin/supervisorctl restart adhocracy_test:test_frontend',
        shell=True,
        stderr=subprocess.STDOUT
    )

    def fin():
        subprocess.check_output(
            'bin/supervisorctl stop adhocracy_test:test_frontend',
            shell=True,
            stderr=subprocess.STDOUT
        )
    request.addfinalizer(fin)

    return output


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


def add_helper_methods_to_splinter_browser_wrapper(inst: Browser) -> Browser:
    """Add additional helper functions to the splinter browser wrapper."""
    inst.compile_js_code = types.MethodType(compile_js_code, inst)
    inst.evaluate_script_with_kwargs = types.MethodType(
        evaluate_script_with_kwargs, inst)
    return inst


def angular_app_loaded(browser: Browser) -> bool:
    """Check that the angular app is loaded."""
    code = 'window.hasOwnProperty("adhocracy") '\
           '&& window.adhocracy.hasOwnProperty("loadState") '\
           '&& window.adhocracy.loadState === "complete";'
    return browser.evaluate_script(code)


@fixture(scope='class')
def tmpdir_class(request):
    """tmpdir with class scope."""
    name = request.node.name
    name = re.sub('[\W]', '_', name)
    maxval = 30
    if len(name) > maxval:
        name = name[:maxval]
    x = request.config._tmpdirhandler.mktemp(name, numbered=True)
    return x


@fixture(scope='class')
def browser_instance_getter_class(request,
                                  browser_patches,
                                  splinter_browser_load_condition,
                                  splinter_browser_load_timeout,
                                  splinter_download_file_types,
                                  splinter_driver_kwargs,
                                  splinter_file_download_dir,
                                  splinter_firefox_profile_preferences,
                                  splinter_make_screenshot_on_failure,
                                  splinter_remote_url,
                                  splinter_screenshot_dir,
                                  splinter_selenium_implicit_wait,
                                  splinter_selenium_socket_timeout,
                                  splinter_selenium_speed,
                                  splinter_webdriver,
                                  splinter_window_size,
                                  tmpdir_class,
                                  browser_pool,
                                  ):
    """Browser instance getter with class scope."""
    return browser_instance_getter(request,
                                   browser_patches,
                                   splinter_browser_load_condition,
                                   splinter_browser_load_timeout,
                                   splinter_download_file_types,
                                   splinter_driver_kwargs,
                                   splinter_file_download_dir,
                                   splinter_firefox_profile_preferences,
                                   splinter_make_screenshot_on_failure,
                                   splinter_remote_url,
                                   splinter_screenshot_dir,
                                   splinter_selenium_implicit_wait,
                                   splinter_selenium_socket_timeout,
                                   splinter_selenium_speed,
                                   splinter_webdriver,
                                   splinter_window_size,
                                   tmpdir_class,
                                   browser_pool,
                                   )


@fixture(scope='class')
def browser_class(request, browser_instance_getter_class):
    """Browser fixture with class scope."""
    return browser_instance_getter_class(browser_class)


@fixture(scope='class')
def browser2_class(request, browser_instance_getter_class):
    """Second Browser fixture with class scope."""
    return browser_instance_getter_class(browser2_class)


@fixture(scope='class')
def browser_root(browser_class, backend, frontend, frontend_url):
    """Return test browser, start application and go to `root.html`.

    Add attribute `root_url` pointing to the adhocracy root.html page.
    Add attribute `app_url` pointing to the adhocracy application page
    """
    add_helper_methods_to_splinter_browser_wrapper(browser_class)
    browser_class.root_url = frontend_url
    browser_class.app_url = frontend_url  # FIXME do we still need this?
    browser_class.visit(frontend_url)
    browser_class.execute_script('window.localStorage.clear();')
    browser_class.wait_for_condition(angular_app_loaded, 5)
    return browser_class


def browser_test_helper(browser, url, wait=5) -> Browser:
    """Return test browser and go to url."""
    add_helper_methods_to_splinter_browser_wrapper(browser)

    browser.visit(url)

    def jasmine_finished(browser):
        code = 'jsApiReporter.finished'
        return browser.evaluate_script(code)

    browser.wait_for_condition(jasmine_finished, wait)

    return browser


@fixture(scope='class')
def browser_test(browser_class, frontend, frontend_url) -> Browser:
    """Return test browser instance with url=test.html."""
    url = frontend_url + 'static/test.html'
    return browser_test_helper(browser_class, url)


@fixture(scope='class')
def browser_igtest(browser_class, backend, frontend, frontend_url) -> Browser:
    """Return test browser instance with url=igtest.html."""
    url = frontend_url + 'static/igtest.html'
    # long timeout to ease debugging, jasmine tests already have a short one
    return browser_test_helper(browser_class, url, wait=180)
