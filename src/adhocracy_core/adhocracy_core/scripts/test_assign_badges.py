from copy import deepcopy

from pyramid import testing
from unittest.mock import Mock
from pytest import fixture

from adhocracy_core.interfaces import IResource

class TestAssignBadges:

    @fixture
    def context(self, pool, service):
        pool['principals'] = service
        pool['principals']['users'] = deepcopy(service)
        pool['organisation'] = deepcopy(pool)
        pool['organisation']['badges'] = service
        return pool

    def test_create_badge_assignment(self, service, context):
        from .assign_badges import _create_badge_assignment
        from substanced.interfaces import IFolder
        import adhocracy_core.resources.badge

        entry = {"user": "/principals/users/0000000",
                 "badge": "/organisation/badges/winning/",
                 "proposalversion": "/organisation/Winning_123/VERSION_0000001/",
                 "proposalitem": "/organisation/Winning_123/",
                 "description" : "## Lorem ipsum"
        }
        user = testing.DummyResource()
        context['principals']['users']['0000000'] = user
        badge = testing.DummyResource()
        context['organisation']['badges']['winning'] = badge
        # without the __provides__, the find_service blocks and does not return!
        proposalitem = testing.DummyResource(__provides__=IFolder)
        context['organisation']['Winning_123'] = proposalitem
        proposalversion = testing.DummyResource()
        context['organisation']['Winning_123']['VERSION_0000001'] = proposalitem
        badge_assignments_service = deepcopy(service)
        context['organisation']['Winning_123']['badge_assignments'] = badge_assignments_service
        registry = Mock()

        _create_badge_assignment(entry, context, registry)

        registry.content.create.assert_called_with(
            adhocracy_core.resources.badge.IBadgeAssignment.__identifier__,
            parent=badge_assignments_service,
            appstructs={'adhocracy_core.sheets.badge.IBadgeAssignment':
                        {'object': proposalitem,
                         'subject': user,
                         'badge': badge},
                        'adhocracy_core.sheets.description.IDescription':
                        {'description': '## Lorem ipsum'}})
