from pyramid import testing
from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources')


class TestDocumentProcess:

    @fixture
    def meta(self):
        from .document_process import document_process_meta
        return document_process_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        assert meta.iresource == resources.document_process.IDocumentProcess
        assert meta.iresource.isOrExtends(resources.process.IProcess)
        assert meta.element_types == [resources.document.IDocument,
                                      ]
        assert meta.is_implicit_addable is True

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
