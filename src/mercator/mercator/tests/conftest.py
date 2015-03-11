"""Add or override py.test fixtures for all tests in this directory."""
from splinter import Browser
from pytest import fixture

from adhocracy_frontend.tests.acceptance.shared import api_login_god
from adhocracy_frontend.tests.acceptance.shared import get_random_string
from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.fixtures.users import create_user


@fixture(scope='class')
def browser(browser_root, backend, frontend, frontend_url) -> Browser:
    """Return test browser, start application and go to `root.html`."""
    return browser_root


@fixture(scope='class')
def user(backend):
    """Create a user via REST API and return (name, password)."""
    name = get_random_string(n=5)
    password = 'password'
    create_user(name, password)
    import time
    time.sleep(1)
    return name, password


@fixture(scope='class')
def proposal(backend):
    """Create a single, random proposal."""
    credentials = api_login_god()
    return create_proposals(user_token=credentials['user_token'],
                            user_path=credentials['user_path'],
                            n=1)


@fixture(scope='class')
def proposals(backend):
    """Create 10 random proposals."""
    credentials = api_login_god()
    return create_proposals(user_token=credentials['user_token'],
                            user_path=credentials['user_path'],
                            n=10)


@fixture(scope='class')
def browser_with_proposal(proposal, browser) -> Browser:
    """Return test browser with a single proposal."""
    assert browser.is_text_present('supporters', wait_time=2)
    return browser


@fixture(scope='class')
def browser_with_proposals(proposals, browser) -> Browser:
    """Return test browser with 10 proposals."""
    assert browser.is_text_present('supporters', wait_time=2)
    return browser
