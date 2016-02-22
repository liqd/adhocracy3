from pyramid.traversal import find_resource
from pyramid import testing
from pytest import fixture
from pytest import mark
from webtest import TestResponse
import transaction

from adhocracy_core.authorization import set_local_roles
from adhocracy_core.authorization import get_acl
from adhocracy_core.authorization import set_acl
from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.utils import get_root
from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to
from adhocracy_core.schema import ACM


@fixture
def integration(integration):
    integration.include('adhocracy_core.workflows')
    return integration

@mark.usefixtures('integration')
def test_includeme(registry):
    from adhocracy_core.workflows import AdhocracyACLWorkflow
    workflow = registry.content.workflows['standard_private']
    assert isinstance(workflow, AdhocracyACLWorkflow)
