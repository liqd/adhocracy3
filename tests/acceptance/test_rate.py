from pytest import fixture
from pytest import mark

from adhocracy_core.testing import annotator_login
from .shared import wait
from .shared import get_column_listing
from .shared import get_list_element
from .shared import get_listing_create_form
from .shared import login_annotator
from .test_proposal import proposal
from .test_comment import comment
from .test_comment import browser


def test_upvote(browser, comment):
    rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
    pro_button = rateable.find_by_css('.rate-pro')
    pro_button.click()
    total = rateable.find_by_css('.rate-difference')
    assert total[0].text is '+1'

def test_downvote(browser, comment):
    rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
    pro_button = rateable.find_by_css('.rate-contra')
    pro_button.click()
    total = rateable.find_by_css('.rate-difference')
    assert total[0].text is '-1'

def test_neutralvote(browser, comment):
    rateable = get_column_listing(browser, 'content2').find_by_css('.comment')
    pro_button = rateable.find_by_css('.rate-neutral')
    pro_button.click()
    total = rateable.find_by_css('.rate-difference')
    assert total[0].text is '0'
