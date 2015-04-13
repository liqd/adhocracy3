from pytest import fixture
from pyramid.security import Allow
from pyramid.security import Deny


def test_disable_add_proposal_permission(context):
    from . import evolve2_disable_add_proposal_permission
    context.__acl__ \
        = [(Allow, 'role:contributor', 'add_proposal'),
           (Allow, 'role:creator', 'add_mercator_proposal_version')]
    evolve2_disable_add_proposal_permission(context)
    assert (Deny, 'role:contributor', 'add_proposal') in context.__acl__
    assert (Deny, 'role:creator', 'add_mercator_proposal_version') \
        in context.__acl__

def test_disable_add_proposal_permission_mark_context_as_dirty(context):
    """set _p_changed attribute true to fix substanced.util.set_acl"""
    from . import evolve2_disable_add_proposal_permission
    context.__acl__ = []
    evolve2_disable_add_proposal_permission(context)
    assert context._p_changed
