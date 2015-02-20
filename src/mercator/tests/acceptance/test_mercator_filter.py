from webtest import TestApp
from pytest import fixture

from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals
from adhocracy_frontend.tests.acceptance.shared import api_login_god
from adhocracy_frontend.tests.acceptance.shared import wait

class TestMercatorFilter(object):

    @fixture(scope='class')
    def sidebar(self, browser):
        return browser.find_by_css('.moving-column-sidebar').first.find_by_tag('ul')

    @fixture(scope='class')
    def locations(self, browser, sidebar):
        return sidebar[1].find_by_tag('li')

    @fixture(scope='class')
    def budgets(self, browser, sidebar):
        return sidebar[2].find_by_tag('li')

    @fixture(scope='class')
    def browser(self, browser, app):
        TestApp(app)
        browser.visit(browser.app_url + 'r/mercator/')
        assert wait(lambda: browser.find_link_by_text('filters'))

        browser.find_link_by_text('filters').first.click()
        assert wait(lambda: browser.find_by_css('.moving-column-sidebar').visible)

        return browser

    def test_filter_location(self, browser, locations, proposals):
        for location in locations:
            location.find_by_css('a').first.click()
            assert wait(lambda:
                is_filtered(browser, proposals, location=location))

    def test_unfilter_location(self, browser, locations, proposals):
        locations[-1].find_by_css('a').first.click()
        assert wait(lambda: is_filtered(browser, proposals))

    def test_filter_budget(self, browser, budgets, proposals):
        for budget in budgets:
            budget.find_by_css('a').first.click()
            assert wait(lambda:
                is_filtered(browser, proposals, budget=budget))

    def test_unfilter_budget(self, browser, budgets, proposals):
        budgets[-1].find_by_css('a').first.click()
        assert wait(lambda: is_filtered(browser, proposals))

    def test_filter_combinations(self, browser, locations, budgets, proposals):
        for location in locations:
            location.find_by_css('a').first.click()
            for budget in budgets:
                budget.find_by_css('a').first.click()
                assert wait(lambda:
                    is_filtered(browser, proposals, location=location,
                                budget=budget))



def is_filtered(browser, proposals, location=None, budget=None):
    try:
        title_sheet = 'adhocracy_mercator.sheets.mercator.ITitle'
        title = lambda p: p[23]['body']['data'][title_sheet]['title']
        expected_titles = [title(p) for p in proposals
            if _verify_location(location, p) and
            _verify_budget(budget, p)]

        proposal_list = browser.find_by_css('.moving-column-body').first.\
                                find_by_tag('ol').first
        actual_titles = [a.text for a in
                proposal_list.find_by_css('.mercator-proposal-list-item-title')]

        return set(expected_titles) == set(actual_titles)
    except:
        # If the DOM still changes there may be StaleElementReferenceExceptions.
        # In that case, we should return False rather than crashing.
        return False


def _verify_location(location, proposal):
    '''Return whether the passed proposal is of given location.'''
    data = proposal[18]['body']['data']
    data_location = data['adhocracy_mercator.sheets.mercator.ILocation']

    if location is None:
        return True

    elif location.has_class('facet-item-specific'):
        return data_location['location_is_specific']

    elif location.has_class('facet-item-online'):
        return data_location['location_is_online']

    elif location.has_class('facet-item-linked_to_ruhr'):
        return data_location['location_is_linked_to_ruhr']

    return False


def _verify_budget(budget, proposal):
    '''Return whether the passed proposal is of given budget.'''
    data = proposal[4]['body']['data']
    finance = data['adhocracy_mercator.sheets.mercator.IFinance']

    if budget is None:
        return True

    elif budget.has_class('facet-item-5000'):
        return 0 <= finance['budget'] <= 5000

    elif budget.has_class('facet-item-10000'):
        return 5000 <= finance['budget'] <= 10000

    elif budget.has_class('facet-item-20000'):
        return 10000 <= finance['budget'] <= 20000

    elif budget.has_class('facet-item-50000'):
        return 20000 <= finance['budget'] <= 50000

    elif budget.has_class('facet-item-above_50000'):
        return finance['budget'] >= 50000

    return False
