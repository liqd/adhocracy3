from pytest import fixture

from .shared import wait
from .shared import get_column_listing
from .shared import get_list_element
from .shared import get_listing_create_form
from .test_proposal import proposal


@fixture
def comment(browser, proposal):
    """Go to content2 column and create comment with content 'comment1'."""
    show_proposal_comments(proposal)
    listing = get_column_listing(browser, 'content2')
    return create_comment(listing, 'comment1')


def test_create(browser, proposal):
    show_proposal_comments(proposal)
    listing = get_column_listing(browser, 'content2')
    comment = create_comment(listing, 'somecomment')
    assert comment is not None


def test_reply(browser, comment):
    listing = get_column_listing(browser, 'content2').find_by_css('.listing')
    element = create_comment(listing, 'somereply')
    assert element is not None


def test_edit(browser, comment):
    edit_comment(comment, 'edited')
    assert comment.find_by_css('.comment-content').text == 'edited'

    browser.reload()

    proposal = browser.find_by_css('.listing-element')
    show_proposal_comments(proposal)
    assert len(browser.find_by_css('.comment-content')) == 1
    assert browser.find_by_css('.comment-content').text == 'edited'


def show_proposal_comments(proposal):
    proposal.find_by_css('a').first.click()
    proposal.find_by_css('button').last.click()


def create_comment(listing, content):
    """Create a new Comment."""
    form = get_listing_create_form(listing)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()
    return get_list_element(listing, content, descendant='.comment-content')


def edit_comment(comment, content):
    comment.find_by_css('a')[-2].click()
    comment.find_by_css('textarea').first.fill(content)
    comment.find_by_css('a')[-3].click()
    wait(lambda: len(comment.find_by_css('a')) == 2)
