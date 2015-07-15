from pytest import fixture
from pytest import mark


class TestDocumentProcess:

    @fixture
    def meta(self):
        from .digital_leben import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from adhocracy_spd import resources
        from adhocracy_spd import sheets
        assert meta.iresource == resources.digital_leben.IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)
        assert meta.extended_sheets == (
            sheets.digital_leben.IWorkflowAssignment,
        )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
