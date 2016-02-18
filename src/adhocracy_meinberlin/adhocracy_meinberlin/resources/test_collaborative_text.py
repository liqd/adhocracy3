from pytest import fixture
from pytest import mark
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to


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

def _post_document_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    resp = app_user.post_resource(path, IDocument, {})
    return resp
