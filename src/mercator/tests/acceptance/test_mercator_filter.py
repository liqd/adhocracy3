from webtest import TestApp
from pytest import fixture
import time

from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.acceptance.shared import wait


@fixture(scope='module')
def proposals():
    return create_proposals()


class TestMercatorFilter(object):

    @fixture(scope='class')
    def sidebar(self, browser):
        return browser.find_by_css(".moving-column-sidebar").first.find_by_tag("ul")

    @fixture(scope='class')
    def locations(self, browser, sidebar):
        return [l.find_by_tag("a").first for l in sidebar[1].find_by_tag("li")]

    @fixture(scope='class')
    def bugdets(self, browser, sidebar):
        return [l.find_by_tag("a").first for l in sidebar[2].find_by_tag("li")]

    @fixture(scope='class')
    def browser(self, browser, app):
        TestApp(app)
        login_god(browser)
        browser.visit(browser.app_url + 'r/mercator/')
        wait(lambda: browser.is_element_present_by_name("filters"))

        browser.find_link_by_text("filters").first.click()
        wait(lambda: browser.find_by_css(".moving-column-sidebar").visible)

        return browser

    def test_filter_location(self, browser, locations, proposals):
        for location in locations:
            location.click()

            #TODO waiting for filtering to complete
            time.sleep(2)

            assert wait(lambda: location_is_filtered(browser, location.html, proposals))


def location_is_filtered(browser, location, proposals):
    """
    In order to verify correct filtering, two steps are needed. First check
    whether every proposal in proposal list has correct location. Second verify
    that no proposal is missing by checking all proposals with the
    corresponding location to be shown in proposal list.

    """
    proposal_list = browser.find_by_css(".moving-column-body").first.find_by_tag("ol").first
    proposal_title_list = [a.html for a in proposal_list.find_by_css("h3 a")]

    for title in proposal_title_list:
        for prop in proposals:
            data = prop[18]["body"]["data"]
            introduction = data["adhocracy_mercator.sheets.mercator.IIntroduction"]

            if title == introduction["title"]:
                assert _verify_location(location, prop)
                break

        else:
            raise AssertionError("Unknown proposal(%s) in propsal list!" % title)

    for prop in proposals:
        data = prop[18]["body"]["data"]
        introduction = data["adhocracy_mercator.sheets.mercator.IIntroduction"]
        prop_title = introduction["title"]

        if _verify_location(location, prop):
            for title in proposal_title_list:
                if title == prop_title:
                    break

            else:
                raise AssertionError("Proposal(%s) is missing in propsal list!" % prop_title)

    return True


def _verify_location(location, proposal):
    """ returns whether the passed proposal is of given location """
    data = proposal[16]["body"]["data"]
    details = data["adhocracy_mercator.sheets.mercator.IDetails"]

    if location == "Specific":
        return details["location_is_specific"]

    elif location == "Online":
        return details["location_is_online"]

    elif location == "Linked to the Ruhr area":
        return details["location_is_linked_to_ruhr"]

    return False
