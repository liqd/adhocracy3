"""Common fixtures for adhocracy_kit."""
from pytest import fixture


@fixture
def integration(integration):
    """Basic includes for integration tests."""
    integration.include('adhocracy_kit.authorization')
    return integration
