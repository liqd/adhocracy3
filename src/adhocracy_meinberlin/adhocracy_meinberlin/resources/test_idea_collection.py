from pytest import mark
from pytest import fixture


class TestProcess:

    @fixture
    def meta(self):
        from .idea_collection import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        from adhocracy_core.resources.asset import add_assets_service
        from .idea_collection import IProcess
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(resources.process.IProcess)
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_process'
        assert meta.extended_sheets == (
            sheets.geo.ILocationReference,
            sheets.image.IImageReference,
        )
        assert add_assets_service in meta.after_creation
        assert meta.permission_create == 'create_process'
        assert meta.workflow_name == 'standard'
        assert meta.element_types == (
            resources.proposal.IGeoProposal,
        )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
