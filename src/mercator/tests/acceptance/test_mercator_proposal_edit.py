from pytest import fixture
from pytest import raises
from webtest import TestApp
from pytest import mark

from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.acceptance.shared import api_login_god
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.acceptance.shared import wait


@fixture(scope='module')
def proposals():
    return create_proposals(user_token=api_login_god(), n=1)


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


def internal_error(browser):
    return browser.is_text_present("Internal Error", wait_time=10)
