from substanced.util import find_service
from pytest import fixture
from pytest import mark
from adhocracy_core.resources.root import IRootPool
from tempfile import mkstemp
import os
import json


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.geo')
    config.include('adhocracy_core.sheets')


@mark.usefixtures('integration')
class TestImportGroups:

    def test_import_groups_create(self, registry):
        from adhocracy_core.scripts.import_groups import _import_groups

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"name": "moderators-xyz", "roles": ["reader"]},
                {"name": "reviewers-xyz", "roles": ["annotator"]}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        groups = find_service(root, 'principals', 'groups')
        _import_groups(root, registry, filename)

        moderators = groups.get('moderators-xyz', None)
        assert moderators is not None
        assert moderators.roles == ['reader']
        reviewers = groups.get('reviewers-xyz', None)
        assert reviewers is not None
        assert reviewers.roles == ['annotator']

    def test_import_groups_update(self, registry):
        from adhocracy_core.scripts.import_groups import _import_groups
        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"name": "moderators-xyz", "roles": ["reader"]},
                {"name": "reviewers-xyz", "roles": ["annotator"]}
            ]))
        root = registry.content.create(IRootPool.__identifier__)
        groups = find_service(root, 'principals', 'groups')
        _import_groups(root, registry, filename)

        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"name": "moderators-xyz", "roles": ["annotator"]}
            ]))
        _import_groups(root, registry, filename)

        moderators = groups.get('moderators-xyz', None)
        assert moderators is not None
        assert moderators.roles == ['annotator']
        reviewers = groups.get('reviewers-xyz', None)
        assert reviewers is not None
        assert reviewers.roles == ['annotator']

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)
