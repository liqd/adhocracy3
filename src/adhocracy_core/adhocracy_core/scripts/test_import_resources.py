from pytest import fixture
from pytest import mark
from tempfile import mkstemp
import os
import json
from adhocracy_core.resources.root import IRootPool
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.utils import get_sheet_field


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.resources.organisation')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.badge')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.resources.root')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.principal')
    config.include('adhocracy_core.resources.organisation')
    config.include('adhocracy_core.resources.geo')
    config.include('adhocracy_core.sheets')


@fixture
def principals(pool_graph_catalog, registry):
    from adhocracy_core.resources.principal import IPrincipalsService
    context = pool_graph_catalog
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
        # try reading
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

    def test_get_resource_info_name(self):
        from adhocracy_core.scripts.import_resources import _get_resource_info_name

        resource_info = {"path": "/",
                         "creator": "god",
                         "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                         "data": {"adhocracy_core.sheets.name.IName":
                                  {"name": "alt-treptow"}}}
        assert _get_resource_info_name(resource_info) == 'alt-treptow'

    def test_get_resource_info_name_noname(self):
        from adhocracy_core.scripts.import_resources import _get_resource_info_name

        resource_info = {"path": "/",
                         "creator": "god",
                         "content_type": "adhocracy_core.resources.organisation.IOrganisation",
                         "data": {}}
        assert _get_resource_info_name(resource_info) is None

    def test_resolve_value(self, registry, principals):
        from adhocracy_core.scripts.import_resources import _resolve_value

        root = registry.content.create(IRootPool.__identifier__)
        appstructs = {'adhocracy_core.sheets.name.IName': {'name': 'orga'}}
        orga = registry.content.create(IOrganisation.__identifier__, root,
                                       appstructs=appstructs, registry=registry)

        assert _resolve_value(42, root) is 42
        assert _resolve_value('/', root) is root
        assert _resolve_value('/orga', root) is orga
        assert _resolve_value(['/orga', '/orga'], root) == [orga, orga]
        assert _resolve_value({'a': '/', 'b': ['/orga', '/orga']}, root) == \
            {'a': root, 'b': [orga, orga]}

    def teardown_method(self, method):
        if hasattr(self, 'tempfd'):
            os.close(self._tempfd)
