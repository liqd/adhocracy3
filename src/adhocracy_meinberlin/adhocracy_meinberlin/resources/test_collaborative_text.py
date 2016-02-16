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


@mark.functional
class TestCollaborativeText:

    @fixture
    def process_url(self):
        return '/organisation/collaborative_text'

    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app_admin.app_router, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_participate_state(self, registry, process_url, app_admin):
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'participate')
        assert resp.status_code == 200

    def test_participate_initiator_creates_document(self,
                                                    registry,
                                                    process_url,
                                                    app_initiator):
        resp = _post_document_item(app_initiator, path=process_url)
        assert resp.status_code == 200
