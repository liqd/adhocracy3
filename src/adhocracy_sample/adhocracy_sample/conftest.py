"""Additional pytest configuration."""
import pytest


def pytest_collection_modifyitems(items):
    """Mark all doctest tests as functional tests."""
    for item in items:
        if '.rst' in item.nodeid:
            item.add_marker(pytest.mark.functional)
