from pytest import mark

from .shared import wait
from .shared import get_column_listing
from .shared import login_god
from .test_comment import create_comment


class TestRate:

    def test_create(self, browser):
        login_god(browser)
        comment = create_comment(browser, 'comment1')
        assert comment is not None

    @mark.skipif(True, reason='pending weil schlechtes wetter')
    def test_upvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment').first
        button = rateable.find_by_css('.rate-pro').first
        button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference').first
            return total.text == '+1'
        assert wait(check_result)

    def test_downvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment').first
        button = rateable.find_by_css('.rate-contra').first
        button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference').first
            return total.text == '-1'
        assert wait(check_result)

    def test_neutralvote(self, browser):
        rateable = get_column_listing(browser, 'content2').find_by_css('.comment').first
        button = rateable.find_by_css('.rate-neutral').first
        button.click()
        def check_result():
            total = rateable.find_by_css('.rate-difference').first
            return total.text == '0'
        assert wait(check_result)

    @mark.skipif(True, reason='pending weil schlechtes wetter')
    def test_detaillist(self, browser):

        # FIXME: the button appears to be surprisingly click
        # resistant.  since we don't have any clues as to why, we
        # postponed the investigations.

        rateable = get_column_listing(browser, 'content2').find_by_css('.comment').first
        button = rateable.find_by_css('.rate-difference').first
        button.click()

        def check_result():
            try:
                audit_trail = rateable.find_by_css('.rate-details').first
                print(audit_trail)
                return 'god' in audit_trail.text and '0' in audit_trail.text
            except Exception as e:
                print(e)
                return False
        assert wait(check_result)

    @mark.skipif(True, reason="pending weil schlechtes wetter")
    def test_multi_rateable(self, browser):

        # FIXME: all rate widgets are totalled over all others.  there is
        # something wrong with the filter for the rating target (object).
        # write a test for that, then fix it!

        pass

    @mark.skipif(True, reason='pending weil schlechtes wetter')
    def test_multi_user(self, browser):

        # FIXME: test many users and more interesting totals and audit
        # trails.

        pass

    @mark.skipif(True, reason='pending weil schlechtes wetter')
    def test_authorisations(self, browser):

        # FIXME: test replacing god user with one that is allowed to
        # rate, but not much more.

        pass
