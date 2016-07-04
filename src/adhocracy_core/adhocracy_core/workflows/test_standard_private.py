from pytest import fixture
from pytest import mark


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration


@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['standard_private']
    assert isinstance(workflow, ACLLocalRolesWorkflow)
