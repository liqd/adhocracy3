from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme_add_standard_workflow(registry):
    from . import ACLLocalRolesWorkflow
    workflow = registry.content.workflows['badge_assignment']
    assert isinstance(workflow, ACLLocalRolesWorkflow)
