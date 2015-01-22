from adhocracy_frontend.tests.acceptance.shared import wait


class TestNavigation(object):
    def test_simple(self, browser_with_proposal):  # FIXME: bad name
        browser = browser_with_proposal

        column_structure = browser.find_by_css('.moving-column-structure').first
        column_content = browser.find_by_css('.moving-column-content').first
        column_content2 = browser.find_by_css('.moving-column-content2').first

        browser.wait_for_condition(lambda browser: column_structure.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content.has_class('is-hide'))
        browser.wait_for_condition(lambda browser: column_content2.has_class('is-hide'))

        browser.find_by_css('.mercator-proposal-list-item-title a').first.click()

        browser.wait_for_condition(lambda browser: column_structure.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content2.has_class('is-hide'))

        browser.find_by_css('.mercator-proposal-cover-show-comments').first.click()

        browser.wait_for_condition(lambda browser: column_structure.has_class('is-collapse'))
        browser.wait_for_condition(lambda browser: column_content.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content2.has_class('is-show'))

        browser.find_by_css('.moving-column-content2 .moving-column-menu-nav a').last.click()

        browser.wait_for_condition(lambda browser: column_structure.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content2.has_class('is-hide'))

        browser.find_by_css('.moving-column-content .moving-column-menu-nav a').last.click()

        browser.wait_for_condition(lambda browser: column_structure.has_class('is-show'))
        browser.wait_for_condition(lambda browser: column_content.has_class('is-hide'))
        browser.wait_for_condition(lambda browser: column_content2.has_class('is-hide'))
