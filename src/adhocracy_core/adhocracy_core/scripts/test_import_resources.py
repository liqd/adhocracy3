from pytest import fixture
from pytest import mark
from tempfile import mkstemp
import os
import json
import pytest
from adhocracy_core.resources.root import IRootPool
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import get_sheet_field



@fixture
def principals(pool_with_catalogs, registry):
    from adhocracy_core.resources.principal import IPrincipalsService
    context = pool_with_catalogs
    inst = registry.content.create(IPrincipalsService.__identifier__,
                                   parent=context)
    return inst


@mark.usefixtures('integration')
class TestImportResources:

    def test_import_resources(self, registry):
        from adhocracy_core.scripts.import_resources import _import_resources

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/",
                 "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "alt-treptow"}}}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        _import_resources(root, registry, filename)
        assert IOrganisation.providedBy(root['alt-treptow'])
        assert get_sheet_field(root['alt-treptow'], IName, 'name') == 'alt-treptow'


    def test_import_resources_invalid_data(self, registry):
        from adhocracy_core.scripts.import_resources import _import_resources
        import colander

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/",
                 "content_type": "adhocracy_core.resources.pool.IPool",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "NameSample"},
                          "adhocracy_core.sheets.title.ITitle":
                          {"title": 42}
                 }}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        with pytest.raises(colander.Invalid):
            _import_resources(root, registry, filename)


    def test_import_resources_already_exists(self, registry):
        from adhocracy_core.scripts.import_resources import _import_resources

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/",
                 "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "alt-treptow"}}}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        _import_resources(root, registry, filename)
        # try readding
        _import_resources(root, registry, filename)
        assert IOrganisation.providedBy(root['alt-treptow'])
        assert get_sheet_field(root['alt-treptow'], IName, 'name') == 'alt-treptow'

    def test_import_resources_already_oneleveldeep(self, registry, principals):
        from adhocracy_core.scripts.import_resources import _import_resources

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/orga",
                 "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "alt-treptow"}}}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        appstructs = {'adhocracy_core.sheets.name.IName': {'name': 'orga'}}
        registry.content.create(IOrganisation.__identifier__, root,
                                appstructs=appstructs, registry=registry)

        _import_resources(root, registry, filename)
        assert IOrganisation.providedBy(root['orga']['alt-treptow'])

    def test_import_resources_set_creator(self, registry):
        from adhocracy_core.scripts.import_resources import _import_resources

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/",
                 "creator": "god",
                 "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "alt-treptow"}}}
            ]))

        root = registry.content.create(IRootPool.__identifier__)
        _import_resources(root, registry, filename)
        assert IOrganisation.providedBy(root['alt-treptow'])
        god = root['principals']['users'].values()[0]
        assert get_sheet_field(root['alt-treptow'], IMetadata, 'creator') == god

    def test_import_resource_create_group(self, registry):
        from adhocracy_core.scripts.import_resources import _import_resources

        (self._tempfd, filename) = mkstemp()
        with open(filename, 'w') as f:
            f.write(json.dumps([
                {"path": "/principals/groups",
                 "content_type": "adhocracy_core.resources.principal.IGroup",
                 "data": {"adhocracy_core.sheets.name.IName":
                          {"name": "moderators-abc"},
                          "adhocracy_core.sheets.principal.IGroup":
                          {"roles": ["creator", "initiator"]}
                 }
                }

            ]))
        root = registry.content.create(IRootPool.__identifier__)
        _import_resources(root, registry, filename)

    def test_get_expected_path(self):
        from adhocracy_core.scripts.import_resources import _get_expected_path

        resource_info = {"path": "/",
                         "data": {"adhocracy_core.sheets.name.IName":
                                  {"name": "alt-treptow"}}}
        assert _get_expected_path(resource_info) == '/alt-treptow'

    def test_get_expected_path_no_name_noname(self):
        from adhocracy_core.scripts.import_resources import _get_expected_path

        resource_info = {"path": "/",
                         "data": {}}
        assert _get_expected_path(resource_info) == ''


    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)
