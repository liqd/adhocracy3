from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.testing import add_resources
from adhocracy_core.testing import do_transition_to


class TestCollaborativeTextProcess:

    @fixture
    def meta(self):
        from .collaborative_text import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from adhocracy_core import sheets
        from .collaborative_text import IProcess
        assert meta.iresource == IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)
        assert meta.default_workflow == 'debate'
        assert meta.extended_sheets == (
            sheets.image.IImageReference,
        )

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
