from pytest import fixture
from pytest import raises
from webtest import TestApp
from pytest import mark

from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.acceptance.shared import get_random_string
from adhocracy_frontend.tests.acceptance.shared import api_login_god
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.fixtures.users import create_user
from adhocracy_frontend.tests.acceptance.shared import login
from adhocracy_frontend.tests.acceptance.shared import wait


@fixture(scope='module')
def proposals():
    return create_proposals(user_token=api_login_god(), n=1)


@fixture(scope='module')
def user():
    name = get_random_string(n=5)
    password = 'password'
    create_user(name, password)
    import time
    time.sleep(1)
    return name, password


class TestMercatorForm:

    @fixture(scope='class')
    def browser(self, browser, proposals):
        wait(lambda: browser.is_text_present("filters"))
        return browser

    @fixture(scope='class')
    def proposal(self, browser):
       proposal_list = browser.find_by_css(".moving-column-body").\
                                first.find_by_tag("ol").first
       proposal_list.find_by_css("h3 a").first.click()

    @mark.xfail
    def test_resubmitting_proposal(self, browser, proposal):
        login_god(browser)
        wait(lambda: browser.find_link_by_text("edit"))

        browser.find_link_by_text("edit").first.click()
        wait(lambda: browser.find_by_name('accept-disclaimer'))

        browser.find_by_name('accept-disclaimer').first.check()
        browser.find_by_css('input[type="submit"]').first.click()
        assert not internal_error(browser)

    def test_editing_foreign_proposals(self, browser, user, proposal):
        login(browser, user[0], user[1])
        assert not browser.is_text_present("edit", wait_time=1)


def internal_error(browser):
    return browser.is_text_present("Internal Error", wait_time=10)
