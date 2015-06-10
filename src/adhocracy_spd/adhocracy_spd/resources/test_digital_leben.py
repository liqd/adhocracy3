from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.badge')
    config.include('adhocracy_spd.resources.digital_leben')


class TestDocumentProcess:

    @fixture
    def meta(self):
        from .digital_leben import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from .digital_leben import IProcess
        assert meta.iresource == IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
