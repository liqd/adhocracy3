from pytest import fixture
from pytest import mark
from adhocracy_core.resources.root import IRootPool
from pyramid.request import Request
from substanced.interfaces import IUserLocator
from tempfile import mkstemp
import os
import json


@mark.usefixtures('integration')
class TestImportUsers:

    def _get_user_locator(self, context, registry):
        request = Request.blank('/dummy')
        locator = registry.getMultiAdapter((context, request), IUserLocator)
        return locator

    @fixture
    def context(self, registry):
        return registry.content.create(IRootPool.__identifier__)

    def call_fut(self, root, registry, filename):
        from adhocracy_core.scripts.import_users import _import_users
        return _import_users(root, registry, filename)

    def test_create(self, context, registry):
        self._tempfd, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'weakpassword1', 'roles': ['contributor'],
                 'groups': ['gods']},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weakpassword2', 'roles': [], 'groups': []}
            ]))
        locator = self._get_user_locator(context, registry)

        self.call_fut(context, registry, filename)

        alice = locator.get_user_by_login('Alice')
        assert alice.active
        bob = locator.get_user_by_login('Bob')
        assert bob.active

    def test_update_same_name(self, context, registry):
        self._tempfd, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'weakpassword1', 'roles': ['contributor'],
                 'groups': ['gods']},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weakpassword2', 'roles': [], 'groups': []}
            ]))
        locator = self._get_user_locator(context, registry)
        self.call_fut(context, registry, filename)
        alice = locator.get_user_by_login('Alice')
        old_password = alice.password
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice.new@example.org',
                 'initial-password': 'newpassword', 'roles': ['reader'],
                 'groups': ['gods']}]))

        self.call_fut(context, registry, filename)

        alice = locator.get_user_by_login('Alice')
        new_password = alice.password
        assert alice.roles == ['reader']
        assert alice.email == 'alice.new@example.org'
        assert new_password == old_password

    def test_create_and_send_password_reset_mail(self, context, registry,
                                                 mock_messenger):
        registry.messenger = mock_messenger
        self._tempfd, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': '', 'roles': [],
                 'groups': ['gods'], 'send_invitation_mail': True},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weak', 'roles': [],
                 'groups': [], 'send_invitation_mail': False},
            ]))
        locator = self._get_user_locator(context, registry)

        self.call_fut(context, registry, filename)

        alice = locator.get_user_by_login('Alice')
        reset = context['principals']['resets'].values()[0]
        assert not mock_messenger.send_password_reset_mail.called
        assert len(mock_messenger.send_invitation_mail.call_args_list) == 1
        mock_messenger.send_invitation_mail.assert_called_with(alice, reset)

    def test_create_and_create_assign_badge(self, context, registry, mock_messenger):
        from adhocracy_core import sheets
        from adhocracy_core.utils import get_sheet
        from adhocracy_core.utils import get_sheet_field
        registry.messenger = mock_messenger
        self._tempfd, filename = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': '', 'roles': [],
                 'groups': ['gods'], 'badges': ['expert']},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weak', 'roles': [],
                 'groups': [], 'badges': ['expert']},
            ]))
        locator = self._get_user_locator(context, registry)

        self.call_fut(context, registry, filename)

        alice = locator.get_user_by_login('Alice')
        assignments = get_sheet_field(alice, sheets.badge.IBadgeable, 'assignments')
        assignment = assignments[0]
        assignment_sheet = get_sheet(assignment, sheets.badge.IBadgeAssignment)
        badge = context['principals']['badges']['expert']
        assert assignment_sheet.get() == {'object': alice,
                                          'badge': badge,
                                          'subject': alice}
        bob = locator.get_user_by_login('Alice')
        assignments = get_sheet_field(bob, sheets.badge.IBadgeable, 'assignments')
        assignment = assignments[0]
        assignment_sheet = get_sheet(assignment, sheets.badge.IBadgeAssignment)
        badge = context['principals']['badges']['expert']
        assert assignment_sheet.get() == {'object': bob,
                                          'badge': badge,
                                          'subject': bob}

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)


