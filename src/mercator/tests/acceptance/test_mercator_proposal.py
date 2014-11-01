from pytest import fixture
from pytest import mark
from webtest import TestApp

from adhocracy_frontend.tests.acceptance.shared import login_god


class TestMercatorForm:

    @fixture(scope='class')
    def browser(self, browser):
        login_god(browser)
        browser.visit(browser.app_url + 'mercator')
        return browser

    def test_fill_all_fields(self, browser):
        fill_all(browser)
        assert can_submit(browser)

    @mark.skipif(True, reason="pending")
    # FIXME: this should work, but: (1) it may alter state and confuse
    # subsequent tests; and (2) i'm not sure if it does even work
    # itself.
    def test_submitting_creates_a_new_proposal(self, browser, app):
        browser.find_by_css('input[type="submit"]').first.click()
        #FIXME make this test shorter and more acceptance test like
        import time
        time.sleep(1)
        app = TestApp(app)
        rest_url = 'http://localhost'
        post_pool = '/adhocracy'

        resp = app.get(rest_url + post_pool)
        assert resp.status_code == 200
        elements = resp.json['data']['adhocracy_core.sheets.pool.IPool']['elements']
        assert len(elements) == 1

    def test_field_extra_exprerience_is_optional(self, browser):
        browser.find_by_name('experience').first.fill('')
        assert can_submit(browser)

    def test_field_status_text_is_not_shown_if_non_custom_status(self, browser):
        browser.find_by_name('organization_info-status_enum').first.check()
        status_text = 'organization_info-status_other'
        assert browser.is_element_not_present_by_name(status_text)
        assert can_submit(browser)

    def test_field_status_text_is_required_if_custom_status(self, browser):
        browser.find_by_name('organization_info-status_enum').last.check()
        status_text = 'organization_info-status_other'
        assert browser.is_element_present_by_name(status_text)
        assert not can_submit(browser)
        browser.find_by_name(status_text).first.fill('statustext')
        assert can_submit(browser)

    def test_field_name_is_required(self, browser):
        browser.find_by_name('user_info-first_name').first.fill('')
        assert not can_submit(browser)



def can_submit(browser):
    return browser.is_element_present_by_css(
        'input[type="submit"]:not(:disabled)')


def fill_all(browser):
    browser.find_by_name('user_info-first_name').first.fill('name')
    browser.find_by_name('user_info-last_name').first.fill('lastname')

    # NOTE: Due to angular magic used in ng-options, the value which is
    # stored in the respective ng-model (e.g. 'DE') isn't reflected in the
    # DOM, and an index is used instead.
    browser.select('user_info-country', '1')

    browser.find_by_name('organization_info-name').first.fill(
        'organisation name')
    browser.find_by_name('organization_info-website').first.fill(
        'http://example.com')
    browser.find_by_name('organization_info-date_of_foreseen_registration')\
        .first.fill('02/2015')
    browser.select('organization_info-country', '2')
    browser.find_by_name('organization_info-status_enum').first.check()

    browser.find_by_name('introduction-title').first.fill('title')
    browser.find_by_name('introduction-teaser').first.fill('teaser')

    browser.find_by_name('details-description').first.fill('description')
    browser.find_by_name('details-location_is_specific').first.check()
    browser.find_by_name('details-location_specific_1').first.fill('Bonn')
    browser.find_by_name('details-location_is_linked_to_ruhr').first.check()
    browser.find_by_name('story').first.fill('story')

    browser.find_by_name('outcome').first.fill('success')
    browser.find_by_name('steps').first.fill('plan')
    browser.find_by_name('value').first.fill('relevance')
    browser.find_by_name('partners').first.fill('partners')

    browser.find_by_name('finance-budget').first.fill(1000)
    browser.find_by_name('finance-requested_funding').first.fill(1000)
    browser.find_by_name('finance-granted').first.check()

    browser.find_by_name('experience').first.fill('experience')
    browser.find_by_name('heard_from-colleague').first.check()
