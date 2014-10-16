from pytest import fixture
from pytest import mark

from adhocracy_core.testing import annotator_login
from .shared import wait
from .shared import get_column_listing
from .shared import get_list_element
from .shared import get_listing_create_form
from .shared import login_god
from .test_comment import create_comment

class TestRate:

    def test_create(self, browser):
        login_god(browser)
        comment = create_comment(browser, 'comment1')
        assert comment is not None

    def test_upvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
        pro_button = rateable.find_by_css('.rate-pro')
        pro_button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference')
            return total[0].text == '+1'
        assert wait(check_result)

    def test_downvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
        pro_button = rateable.find_by_css('.rate-contra')
        pro_button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference')
            return total[0].text == '-1'
        assert wait(check_result)

    def test_neutralvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
        pro_button = rateable.find_by_css('.rate-neutral')
        pro_button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference')
            return total[0].text == '0'
        assert wait(check_result)

    # FIXME: test detail list.

    # FIXME: test replacing god user with one that is allowed to rate, but not much more.

    # FIXME: test manu users and more interesting totals.
