from urllib.parse import urlencode

from pytest import fixture
from pytest import mark

from adhocracy_core.testing import god_login
from adhocracy_frontend.tests.acceptance.shared import wait
from adhocracy_frontend.tests.acceptance.shared import get_list_element
from adhocracy_frontend.tests.acceptance.shared import get_listing_create_form
from adhocracy_frontend.tests.acceptance.shared import get_random_string
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.fixtures.users import create_user
from adhocracy_frontend.tests.acceptance.shared import logout
from adhocracy_frontend.tests.acceptance.shared import login


EDIT = 'edit'
REPLY = 'reply'
SAVE = 'save'

@fixture(scope='module')
def user():
    name = get_random_string(n=5)
    password = 'password'
    create_user(name, password)
    import time
    time.sleep(1)
    return name, password


class TestComment:

    def test_create(self, browser, rest_url):
        login_god(browser)
        comment = create_comment(browser, rest_url, 'comment1')
        assert comment is not None

    def test_empty_comment(self, browser, rest_url):
        comment = create_comment(browser, rest_url, '')
        assert comment is None

    def test_nested_replies(self, browser, n=3):
        for i in range(n):
            comment = browser.find_by_css('.comment').last
            reply = create_reply_comment(browser, comment, 'nested reply %d' % i)
            assert reply is not None

    def test_multiple_replies(self, browser, n=3):
        comment = browser.find_by_css('.comment').first
        for i in range(n):
            reply = create_reply_comment(browser, comment, 'multiple reply %d' % i)
            assert reply is not None

    def test_edit(self, browser):
        comment = browser.find_by_css('.comment').first
        edit_comment(browser, comment, 'edited')
        assert comment.find_by_css('.comment-content').first.text == 'edited'

        browser.reload()

        assert wait(lambda: browser.find_by_css('.comment-content')
                                   .first.text == 'edited')

    @mark.xfail(reason='Random timeouts')
    def test_edit_twice(self, browser):
        comment = browser.find_by_css('.comment').first
        edit_comment(browser, comment, 'edited 1')
        assert wait(lambda: comment.find_by_css('.comment-content')
                    .first.text == 'edited 1')
        edit_comment(browser, comment, 'edited 2')
        assert wait(lambda: comment.find_by_css('.comment-content')
                    .first.text == 'edited 2')

    def test_multi_edits(self, browser):
        parent = browser.find_by_css('.comment').first
        reply = parent.find_by_css('.comment').first
        edit_comment(browser, reply, 'somereply edited')
        edit_comment(browser, parent, 'edited')
        assert wait(lambda: parent.find_by_css('.comment-content')
                                  .first.text == 'edited')

    def test_author(self, browser):
        comment = browser.find_by_css('.comment').first
        actual = lambda element: element.find_by_css('adh-user-meta').first.text
        # the captialisation might be changed by CSS
        assert wait(lambda: actual(comment).lower() == god_login.lower())

    def test_edit_no_user(self, browser, rest_url, user):
        logout(browser)
        comment = browser.find_by_css('.comment').first
        assert not _get_button(browser, comment, EDIT)

    def test_reply_no_user(self, browser):
        comment = browser.find_by_css('.comment').last
        assert not _get_button(browser, comment, REPLY)

    @mark.xfail(reason='Random timeouts')
    def test_edit_other_user(self, browser, rest_url, user):
        login(browser, user[0], user[1])
        _visit_url(browser, rest_url)
        assert browser.is_text_present('edited')
        comment = browser.find_by_css('.comment').first
        assert not _get_button(browser, comment, EDIT)

    @mark.xfail(reason='Random timeouts')
    def test_reply_other_user(self, browser):
        comment = browser.find_by_css('.comment').first
        reply = create_reply_comment(browser, comment, 'other user reply')
        assert reply is not None


def _visit_url(browser, rest_url):
    query = urlencode({
        'key': 'test',
        'pool-path': rest_url + 'adhocracy/',
    })
    browser.visit(browser.app_url + 'embed/create-or-show-comment-listing?' + query)


def create_comment(browser, rest_url, name):
    """Go to content2 column and create comment with content 'comment1'."""
    _visit_url(browser, rest_url)
    browser.is_element_present_by_css('.listing', wait_time=10)
    listing = browser.find_by_css('.listing').first
    comment = create_top_level_comment(browser, listing,  name)
    return comment


def create_top_level_comment(browser, listing, content):
    """Create a new top level Comment."""
    form = get_listing_create_form(listing)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()
    browser.is_text_present(content, wait_time=10)
    comment = get_list_element(listing, content, descendant='.comment-content')
    return comment


def create_reply_comment(browser, parent, content):
    """Create a new reply to an existing comment."""
    form = get_comment_create_form(browser, parent)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()
    if not browser.is_text_present(content, wait_time=15):
        return None
    reply = get_reply(parent, content)
    return reply


def _get_button(browser, comment, text):
    actions = comment.find_by_css('.comment-header-links a')\
              + comment.find_by_css('.comment-actions a')

    for a in actions:
        if a.text == text:
            return a
    else:
        return None


def edit_comment(browser, comment, content):
    edit = _get_button(browser, comment, EDIT)
    assert edit
    edit.click()

    comment.find_by_css('.comment-edit-form-text').first.fill(content)
    save = comment.find_by_css('.comment-children-edit-form .form-footer-button-cta').first
    assert save
    save.click()
    browser.is_text_present(content, wait_time=10)


def get_comment_create_form(browser, comment):
    reply = _get_button(browser, comment, REPLY)
    assert reply
    reply.click()
    return comment.find_by_css('.comment-create-form').first


def get_reply(parent, content):
    """Return reply to comment `parent` with content == `content`."""
    for element in parent.find_by_css('.comment'):
        wait(lambda: element.text, max_steps=100)
        if element.find_by_css('.comment-content').first.text == content:
            return element
