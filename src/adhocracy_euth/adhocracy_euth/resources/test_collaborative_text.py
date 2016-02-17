from pytest import fixture
from pytest import mark


class TestCollaborativeTextProcess:

    @fixture
    def meta(self):
        from .collaborative_text import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from .collaborative_text import IProcess
        assert meta.iresource == IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)
        assert meta.workflow_name == 'debate'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestPrivateCollaborativeTextProcess:

    @fixture
    def meta(self):
        from .collaborative_text import private_process_meta
        return private_process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from .collaborative_text import IPrivateProcess
        assert meta.iresource == IPrivateProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)
        assert meta.workflow_name == 'debate_private'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
