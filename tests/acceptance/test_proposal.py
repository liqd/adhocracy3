from pytest import fixture

from .shared import wait
from .shared import get_listing_create_form


def create(listing, title, description='', paragraphs=[]):
    """Create a new Proposal."""
    form = get_listing_create_form(listing)

    form.find_by_css('[name="title"]').first.fill(title)
    form.find_by_css('[name="description"]').first.fill(description)
    for paragraph in paragraphs:
        form.find_by_css('[name="add-paragraph"]').first.click()
        form.find_by_css('textarea')[-1].fill(paragraph)

    form.find_by_css('input[type="submit"]').first.click()


@fixture
def proposal(browser):
    column = '.moving-column-content'
    listing = browser.browser.find_by_css(column + ' .listing').first

    create(listing, 'test proposal')

    browser.browser.is_element_present_by_css(column + ' .listing-element')
    element = listing.find_by_css('.listing-element')
    wait(lambda: element.text)

    return element


def test_create(browser):
    column = '.moving-column-content'
    listing = browser.browser.find_by_css(column + ' .listing').first

    create(listing, 'sometitle')

    assert browser.browser.is_element_present_by_css(
        column + ' .listing-element')

    element = listing.find_by_css('.listing-element')
    element_a = element.find_by_css('a').first
    assert wait(lambda: element_a.text)
    assert element_a.text == 'sometitle'

    element_a.click()
    assert element.find_by_css('h1').first.text == 'sometitle'
