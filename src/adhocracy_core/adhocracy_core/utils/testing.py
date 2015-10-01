"""Functionalities to ease the testing of Adhocracy."""

import transaction

from pyramid.router import Router

from adhocracy_core.scripts import import_resources
from adhocracy_core.utils import get_root


def add_resources(app: Router, filename: str):
    """Add resources from a JSON file to the app."""
    root = get_root(app)
    import_resources(root, app.registry, filename)
    transaction.commit()
