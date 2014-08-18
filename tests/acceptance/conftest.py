"""Add or override py.test fixtures for all tests in this directory."""
from pytest import fixture


@fixture(scope='class')
def server(server_sample):
    """Return the adhocracy sample app wsgi application."""
    return server_sample


@fixture()
def browser(browsera, server):
    """Return  test browser instance with url=root.html."""
    url = server.application_url + 'frontend_static/root.html'
    browsera.visit(url)

    def angular_app_loaded(browser):
        code = 'window.hasOwnProperty("adhocracy") && window.adhocracy.hasOwnProperty("loadState") && window.adhocracy.loadState === "complete";'  # noqa
        return browser.evaluate_script(code)
    browsera.wait_for_condition(angular_app_loaded, 5)

    return browsera
