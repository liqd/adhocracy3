"""Notify users about activities."""


def includeme(config):
    """Include subscribers."""
    config.include('.subscribers')
