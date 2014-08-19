from pytest import fixture

from .shared import wait
from .shared import get_listing_create_form
from .test_proposal import proposal


def show_proposal_comments(proposal):
    proposal.find_by_css('a').first.click()
    proposal.find_by_css('button').last.click()


def create(listing, content):
    """Create a new Comment."""
    form = get_listing_create_form(listing)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()


def edit(comment, content):
    comment.find_by_css('a')[-2].click()
    comment.find_by_css('textarea').first.fill(content)
    comment.find_by_css('a')[-3].click()
    wait(lambda: len(comment.find_by_css('a')) == 2)


@fixture
def comment(browser, server_sample, proposal):
    show_proposal_comments(proposal)
    column = '.moving-column-content2'
    listing = browser.browser.find_by_css(column + ' .listing').first
    create(listing, 'comment1')

    browser.browser.is_element_present_by_css(column + ' .listing-element')
    element = listing.find_by_css('.listing-element')
    wait(lambda: element.text)

    return element


def test_create(browser, proposal):
    show_proposal_comments(proposal)
    column = '.moving-column-content2'
    listing = browser.browser.find_by_css(column + ' .listing').first

    create(listing, 'somecomment')

    assert browser.browser.is_element_present_by_css(
        column + ' .listing-element')
    element = listing.find_by_css('.listing-element')
    assert wait(lambda: element.text)

    assert element.find_by_css('.comment-content').text == 'somecomment'


def test_reply(browser, comment):
    column = '.moving-column-content2'
    listing = comment.find_by_css('.listing').first
    create(listing, 'somereply')

    assert browser.browser.is_element_present_by_css(
        column + ' .listing-element .listing-element')
    element = listing.find_by_css('.listing-element')
    assert wait(lambda: element.text)

    assert element.find_by_css('.comment-content').text == 'somereply'


def test_edit(browser, comment):
    edit(comment, 'edited')
    assert comment.find_by_css('.comment-content').text == 'edited'

    browser.reload()

    proposal = browser.find_by_css('.listing-element')
    show_proposal_comments(proposal)
    assert len(browser.find_by_css('.comment-content')) == 1
    assert browser.find_by_css('.comment-content').text == 'edited'
