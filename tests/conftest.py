"""Add or override py.test fixtures for all tests in this directory."""
from splinter import Browser
from pytest import fixture
from pytest import skip
import subprocess


def pytest_addoption(parser):
    """Add pytest option --run_embed_tests."""
    parser.addoption('--run_embed_tests', action='store_true', default=False,
                     help='run embed tests (needs /etc/hosts modifications)',
                     )


def pytest_runtest_setup(item):
    """Skip tests with `embed` marker if `--run_embed_tests` is not set."""
    run_embed = item.config.getoption('--run_embed_tests')
    embed_marker = item.get_marker('embed')
    if run_embed:
        return
    elif embed_marker:
        skip('You need to enable embed test with --run_embed_tests')


@fixture(scope='class')
def app(settings):
    """Return the adhocracy wsgi application.

    This overrides adhocracy_core.testing.app.
    """
    from pyramid.config import Configurator
    from adhocracy_core.testing import includeme_root_with_test_users
    import mercator
    settings['adhocracy.add_default_group'] = False
    settings['zodbconn.uri'] = 'memory://'
    settings['adhocracy.ws_url'] = ''
    configurator = Configurator(settings=settings,
                                root_factory=mercator.root_factory)
    configurator.include(mercator)
    configurator.commit()
    configurator.include(includeme_root_with_test_users)
    app = configurator.make_wsgi_app()
    return app


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


@fixture(scope='class')
def browser(browser_class, backend, frontend, frontend_url):
    """Return test browser, start sample application and go to `root.html`.

    Add attribute `root_url` pointing to the adhocracy root.html page.
    Add attribute `app_url` pointing to the adhocracy application page.
    Before visiting a new url the browser waits until the angular app is loaded
    """
    from adhocracy_frontend.testing import angular_app_loaded
    browser_class.root_url = frontend_url
    browser_class.app_url = frontend_url
    browser_class.visit(browser_class.root_url)
    browser_class.execute_script('window.localStorage.clear();')
    browser_class.wait_for_condition(angular_app_loaded, 5)
    return browser_class


@fixture(scope='class')
def browser_embed(browser_class, backend, frontend, frontend_url) -> Browser:
    """Start embedder application."""
    url = frontend_url + 'static/embed.html'
    browser.visit(url)
    return browser
