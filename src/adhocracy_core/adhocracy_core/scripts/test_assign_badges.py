import os
from copy import deepcopy

from pyramid import testing
from unittest.mock import Mock
from pytest import fixture


class TestAssignBadges:

    @fixture
    def context(self, pool, service):
        from substanced.interfaces import IFolder
        pool['principals'] = service
        pool['principals']['users'] = deepcopy(service)
        pool['organisation'] = deepcopy(pool)
        pool['organisation']['badges'] = service
        user = testing.DummyResource()
        pool['principals']['users']['0000000'] = user
        badge = testing.DummyResource()
        pool['organisation']['badges']['winning'] = badge
        # without the __provides__, the find_service blocks and does not return!
        item = testing.DummyResource(__provides__=IFolder)
        pool['organisation']['Winning_123'] = item
        badgeable = testing.DummyResource()
        pool['organisation']['Winning_123']['VERSION_0000001'] = badgeable
        badge_assignments_service = deepcopy(service)
        pool['organisation']['Winning_123']['badge_assignments'] = badge_assignments_service
        return pool

    def write_json(self):
        import json
        from tempfile import mkstemp

        self._tempfd, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                 {"user": "/principals/users/0000000",
                 "badge": "/organisation/badges/winning/",
                 "badgeable": "/organisation/Winning_123/VERSION_0000001/",
                 "description" : "## Lorem ipsum"
                }
            ]))
        return filename

    def test_create_badge_assignment(self, context):
        from .assign_badges import _import_assignments
        import adhocracy_core.resources.badge

        filename = self.write_json()
        registry = Mock()

        _import_assignments(context, registry, filename)

        user = context['principals']['users']['0000000']
        badge = context['organisation']['badges']['winning']
        badgeable = context['organisation']['Winning_123']['VERSION_0000001']
        badge_assignments_service = context['organisation']['Winning_123']['badge_assignments']

        registry.content.create.assert_called_with(
            adhocracy_core.resources.badge.IBadgeAssignment.__identifier__,
            parent=badge_assignments_service,
            appstructs={'adhocracy_core.sheets.badge.IBadgeAssignment':
                        {'object': badgeable,
                         'subject': user,
                         'badge': badge},
                        'adhocracy_core.sheets.description.IDescription':
                        {'description': '## Lorem ipsum'}})

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)

