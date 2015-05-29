from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.sheets.geo')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.badge')


class TestProcess:

    @fixture
    def meta(self):
        from .process import process_meta
        return process_meta

    def test_meta(self, meta):
        from .process import IProcess
        from .asset import add_assets_service
        from .badge import add_badges_service
        from adhocracy_core.interfaces import IPool
        from adhocracy_core import sheets
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(IPool)
        assert meta.is_implicit_addable is False
        assert meta.permission_create == 'create_process'
        assert sheets.asset.IHasAssetPool in meta.basic_sheets
        assert sheets.badge.IHasBadgesPool in meta.basic_sheets
        assert meta.extended_sheets == [sheets.workflow.ISample]
        assert add_assets_service in meta.after_creation
        assert add_badges_service in meta.after_creation


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
