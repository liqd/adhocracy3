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

    def test_update(self, context, registry):
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
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'newpassword', 'roles': ['reader'],
                 'groups': ['gods']}]))

        self.call_fut(context, registry, filename)

        alice = locator.get_user_by_login('Alice')
        new_password = alice.password
        assert alice.roles == ['reader']
        assert new_password == old_password

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)


