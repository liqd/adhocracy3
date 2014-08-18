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
def proposal(browser, server_sample):
    root_url = server_sample.application_url + 'frontend_static/root.html'
    browser.visit(root_url)

    column = '.moving-column-content'
    listing = browser.browser.find_by_css(column + ' .listing').first

    create(listing, 'test proposal')

    browser.browser.is_element_present_by_css(column + ' .listing-element')
    element = listing.find_by_css('.listing-element')
    wait(lambda: element.text)

    return element


def test_create(browser, server):
    register_url = server.application_url + 'frontend_static/root.html'
    browser.visit(register_url)

    column = '.moving-column-content'
    listing = browser.browser.find_by_css(column + ' .listing').first

    create(listing, 'sometitle')

    # FIXME Proposal creation is too slow!! (often takes more than 1sec)
    # This will hopefully be fixed by the batch+high-level API.
    # After fixing, the higher wait_time attribute should be removed.
    assert browser.browser.is_element_present_by_css(
        column + ' .listing-element',
        wait_time=5)

    element = listing.find_by_css('.listing-element')
    element_a = element.find_by_css('a').first
    # FIXME Remove max_steps param once proposal creation is faster, see
    # above!!
    assert wait(lambda: element_a.text, max_steps=20)
    assert element_a.text == 'sometitle'

    element_a.click()
    assert element.find_by_css('h1').first.text == 'sometitle'
