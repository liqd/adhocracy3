"""Shared acceptance test functions."""

from time import sleep


def wait(condition, step=0.1, max_steps=10):
    """Wait for a condition to become true."""
    for i in range(max_steps):
        if condition():
            return True
        sleep(step)
    return condition()


def get_listing_create_form(listing):
    """Open and return the create form of a listing."""
    listing.find_by_css('.navbar .button').first.click()
    return listing.find_by_css('.listing-create-form').first