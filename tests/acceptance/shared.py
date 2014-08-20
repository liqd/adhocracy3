"""Shared acceptance test functions."""
from splinter.driver.webdriver import WebDriverElement

from time import sleep


def wait(condition, step=0.1, max_steps=10) -> bool:
    """Wait for a condition to become true."""
    for i in range(max_steps - 1):
        if condition():
            return True
        else:
            sleep(step)
    return condition()


def fill_input(browser, css_selector, value):
    """Find `css_selector` and fill value."""
    element = browser.browser.find_by_css(css_selector).first
    element.fill(value)


def click_button(browser, css_selector):
    """Find `css_selector` and click."""
    element = browser.browser.find_by_css(css_selector).first
    element.click()


def title_is_in_listing(listing, title: str) -> bool:
    """Check that a listing element with text == `title` exists."""
    for element in listing.find_by_css('.listing-element'):
        wait(lambda: element.text, max_steps=5)
        if element.text == title:
            return True


def get_listing_create_form(listing) -> WebDriverElement:
    """Open and return the create form of a listing."""
    button = listing.find_by_css('.navbar .button').first
    wait(lambda: button.visible)
    button.click()
    return listing.find_by_css('.listing-create-form').first


def get_content_listing(browser) -> WebDriverElement:
    """Return the listing in the content column ."""
    content_column = browser.browser.find_by_css('.moving-column-content')
    listing = content_column.find_by_css('.listing')
    return listing


def get_list_element(listing, title):
    """Return list element with text == `title`."""
    for element in listing.find_by_css('.listing-element'):
        wait(lambda: element.text, max_steps=20)
        if element.text == title:
            return element
