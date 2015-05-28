from pyramid import testing
from tempfile import mkstemp
import os
import json


class TestImportLocalRoles:

    def test_import_local_roles(self, registry):
        from adhocracy_core.scripts.import_local_roles import _import_local_roles

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/alt-treptow",
                 "roles": {"initiators-treptow-koepenick": ["role:initiator"]}}
            ]))

        root = testing.DummyResource()
        root['alt-treptow'] = testing.DummyResource(__parent__=root)
        _import_local_roles(root, registry, filename)
        assert root['alt-treptow'].__local_roles__ == \
            {'initiators-treptow-koepenick': set(['role:initiator'])}

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)
