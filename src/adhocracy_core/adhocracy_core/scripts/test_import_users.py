from pytest import fixture
from pytest import mark
from adhocracy_core.resources.root import IRootPool
from pyramid.request import Request
from substanced.interfaces import IUserLocator
from tempfile import mkstemp
import os
import json


@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources')


@mark.usefixtures('integration')
class TestImportUsers:

    def test_import_users_create(self, registry):
        from adhocracy_core.scripts.import_users import _import_users

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'weakpassword1', 'roles': ['contributor'],
                 'groups': ['gods']},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weakpassword2', 'roles': [], 'groups': []}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        locator = self._get_user_locator(root, registry)
        _import_users(root, registry, filename)

        assert locator.get_user_by_login('Alice') is not None
        assert locator.get_user_by_login('Bob') is not None

    def test_import_users_update(self, registry):
        from adhocracy_core.scripts.import_users import _import_users
        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'weakpassword1', 'roles': ['contributor'],
                 'groups': ['gods']},
                {'name': 'Bob', 'email': 'bob@example.org',
                 'initial-password': 'weakpassword2', 'roles': [], 'groups': []}
            ]))
        root = registry.content.create(IRootPool.__identifier__)
        locator = self._get_user_locator(root, registry)
        _import_users(root, registry, filename)
        alice = locator.get_user_by_login('Alice')
        old_password = alice.password
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {'name': 'Alice', 'email': 'alice@example.org',
                 'initial-password': 'newpassword', 'roles': ['reader'],
                 'groups': ['gods']}]))
        _import_users(root, registry, filename)
        alice = locator.get_user_by_login('Alice')
        new_password = alice.password
        assert alice.roles == ['reader']
        assert new_password == old_password

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)

    def _get_user_locator(self, context, registry):
        request = Request.blank('/dummy')
        locator = registry.getMultiAdapter((context, request), IUserLocator)
        return locator
