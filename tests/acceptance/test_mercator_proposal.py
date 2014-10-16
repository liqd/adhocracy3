from pytest import fixture




class TestMercatorForm:

    @fixture(scope='class')
    def browser(self, browser):
        browser.visit(browser.app_url + 'mercator')
        return browser

    def test_fill_all_fields(self, browser):
        fill_all(browser)
        assert can_submit(browser)

    def test_field_extra_exprerience_is_optional(self, browser):
        browser.find_by_name('extra-experience').first.fill('')
        assert can_submit(browser)

    def test_field_status_text_is_not_shown_if_non_custom_status(self, browser):
        browser.find_by_name('basic-organisation-status').first.check()
        status_text = 'basic-organisation-statustext'
        assert browser.is_element_not_present_by_name(status_text)
        assert can_submit(browser)

    def test_field_status_text_is_required_if_custom_status(self, browser):
        browser.find_by_name('basic-organisation-status').last.check()
        status_text = 'basic-organisation-statustext'
        assert browser.is_element_present_by_name(status_text)
        assert not can_submit(browser)
        browser.find_by_name(status_text).first.fill('statustext')
        assert can_submit(browser)

    def test_field_name_is_required(self, browser):
        browser.find_by_name('basic-user-name').first.fill('')
        assert not can_submit(browser)



def can_submit(browser):
    return browser.is_element_present_by_css(
        'input[type="submit"]:not(:disabled)')


def fill_all(browser):
    browser.find_by_name('basic-user-name').first.fill('name')
    browser.find_by_name('basic-user-lastname').first.fill('lastname')
    browser.find_by_name('basic-user-email').first.fill(
        'name.lastname@domain.com')

    browser.find_by_name('basic-organisation-name').first.fill(
        'organisation name')
    browser.find_by_name('basic-organisation-email').first.fill(
        'info@domain.com')
    browser.find_by_name('basic-organisation-address').first.fill('address')
    browser.find_by_name('basic-organisation-postcode').first.fill('12345')
    browser.find_by_name('basic-organisation-city').first.fill('city')
    browser.select('basic-organisation-country', 'DE')
    browser.find_by_name('basic-organisation-status').first.check()
    browser.find_by_name('basic-organisation-description').first.fill('about')
    browser.find_by_name('basic-organisation-size').first.check()
    browser.find_by_name('basic-organisation-cooperation').last.check()

    browser.find_by_name('introduction-title').first.fill('title')
    browser.find_by_name('introduction-teaser').first.fill('teaser')

    browser.find_by_name('detail-description').first.fill('description')
    browser.find_by_name('detail-location-city').first.check()
    browser.find_by_name('detail-location-ruhr').first.check()
    browser.find_by_name('detail-story').first.fill('story')

    browser.find_by_name('motivation-outcome').first.fill('success')
    browser.find_by_name('motivation-steps').first.fill('plan')
    browser.find_by_name('motivation-value').first.fill('relevance')
    browser.find_by_name('motivation-partners').first.fill('partners')

    browser.find_by_name('finance-budget').first.fill(1000)
    browser.find_by_name('finance-funding').first.fill(1000)
    browser.find_by_name('finance-granted').first.check()

    browser.find_by_name('extra-experience').first.fill('experience')
    browser.find_by_name('extra-experience').first.fill('experience')
    browser.find_by_name('extra-hear-colleague').first.check()
