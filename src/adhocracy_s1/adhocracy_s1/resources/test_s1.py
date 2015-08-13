from pytest import fixture
from pytest import mark


class TestS1Process:

    @fixture
    def meta(self):
        from .s1 import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from adhocracy_s1 import resources
        assert meta.iresource == resources.s1.IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.process.IProcess)
        assert meta.workflow_name== 's1'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
