"""Common fixtures for adhocracy_pcompass."""
from pytest import fixture


@fixture
def integration(integration):
    """Include resource types and sheets."""
    integration.include('adhocracy_pcompass.resources')
    return integration
