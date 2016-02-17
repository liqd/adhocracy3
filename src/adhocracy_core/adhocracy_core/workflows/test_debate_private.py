from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['debate_private']
    assert isinstance(workflow, AdhocracyACLWorkflow)
