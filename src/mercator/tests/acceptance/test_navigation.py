from adhocracy_frontend.tests.acceptance.shared import wait


class TestNavigation(object):

    def test_simple(self, browser_with_proposal):
        browser = browser_with_proposal

        column1 = browser.find_by_css('.moving-column')[0]
        column2 = browser.find_by_css('.moving-column')[1]
        column3 = browser.find_by_css('.moving-column')[2]

        browser.wait_for_condition(lambda browser: column1.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column2.has_class('is-hide'))
        browser.wait_for_condition(lambda browser: column3.has_class('is-hide'))

        browser.find_by_css('.mercator-proposal-list-item').first.click()

        browser.wait_for_condition(lambda browser: column1.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column2.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column3.has_class('is-hide'))

        browser.find_by_css('.mercator-proposal-cover-show-comments').first.click()

        browser.wait_for_condition(lambda browser: column1.has_class('is-collapse'))
        browser.wait_for_condition(lambda browser: column2.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column3.has_class('is-show'))

        column3.find_by_css('.moving-column-menu-nav a').last.click()

        browser.wait_for_condition(lambda browser: column1.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column2.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column3.has_class('is-hide'))

        column2.find_by_css('.moving-column-menu-nav a').last.click()

        browser.wait_for_condition(lambda browser: column1.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column2.has_class('is-hide'))
        browser.wait_for_condition(lambda browser: column3.has_class('is-hide'))
