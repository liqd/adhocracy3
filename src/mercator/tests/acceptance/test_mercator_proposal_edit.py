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
    creds = api_login_god()
    return create_proposals(creds['user_path'], creds['user_token'], n=1)

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
        browser.reload()  # make sure proposals are loaded
        assert browser.is_text_present("supporters", wait_time=2)
        return browser

    def test_edit_proposal_no_user(self, browser):
        select_proposal(browser)
        assert not browser.is_text_present("edit")

    @mark.xfail
    def test_edit_proposal_other_user(self, browser, user):
        login(browser, user[0], user[1])
        select_proposal(browser)

        assert not browser.is_text_present("edit")

    @mark.xfail
    def test_resubmitting_proposal(self, browser):
        login_god(browser)
        select_proposal(browser)

        assert wait(lambda: browser.find_link_by_text("edit"))

        browser.find_link_by_text("edit").first.click()
        assert wait(lambda: browser.find_by_name('accept-disclaimer'))

        browser.find_by_name('accept-disclaimer').first.check()
        browser.find_by_css('input[type="submit"]').first.click()
        assert success(browser)


def success(browser):
    return wait(lambda: browser.url.endswith("/r/mercator/"))


def select_proposal(browser):
    """First click on proposal title in proposal list column and wait until
    proposal is properly loaded in content column. In order to verify proper
    proposal loading, check for the detail's commentary link to contain the
    correct proposal title."""
    proposal_list = browser.find_by_css(".moving-column-body").\
                            first.find_by_tag("ol").first
    proposal_title = proposal_list.find_by_css("h3 a").first
    assert wait(lambda: proposal_title.html)
    proposal_title.click()

    link = browser.find_by_css(".moving-column-content").first.\
                   find_by_css(".mercator-proposal-detail-cover h1 a")
    assert wait(lambda: proposal_title.html in link["href"])
