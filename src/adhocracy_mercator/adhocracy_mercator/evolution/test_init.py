from pytest import fixture
from pyramid.security import Allow
from pyramid.security import Deny


def test_disable_add_proposal_permission(context):
    """Add Deny permissions to start of context.__acl__ to override Allow."""
    from . import evolve2_disable_add_proposal_permission
    context.__acl__ = [(Allow, 'role:contributor', 'add_proposal')]
    evolve2_disable_add_proposal_permission(context)
    assert context.__acl__[0] == (Deny, 'role:contributor', 'add_proposal')
    assert context.__acl__[1] == (Deny, 'role:creator',
                                  'edit_mercator_proposal')


def test_disable_add_proposal_permission_mark_context_as_dirty(context):
    """set _p_changed attribute true to fix substanced.util.set_acl"""
    from . import evolve2_disable_add_proposal_permission
    context.__acl__ = []
    evolve2_disable_add_proposal_permission(context)
    assert context._p_changed


def test_disable_voting_and_commenting(context):
    from . import evolve4_disable_voting_and_commenting
    context.__acl__ = []
    to_disable = set([(Deny, 'role:annotator', 'add_rate'),
                      (Deny, 'role:annotator', 'add_comment'),
                      (Deny, 'role:creator', 'edit_comment'),
                      (Deny, 'role:creator', 'edit_rate')])
    evolve4_disable_voting_and_commenting(context)
    assert set(context.__acl__[:4]) == to_disable
