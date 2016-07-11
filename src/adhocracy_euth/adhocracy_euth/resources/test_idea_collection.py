from pytest import mark
from pytest import fixture
from webtest import TestResponse


class TestProcess:

    @fixture
    def meta(self):
        from .idea_collection import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.proposal import IProposal
        assert meta.element_types == (IProposal,)
        assert meta.default_workflow == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestPrivateProcess:

    @fixture
    def meta(self):
        from .idea_collection import private_process_meta
        return private_process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.proposal import IProposal
        assert meta.element_types == (IProposal,)
        assert meta.default_workflow == 'standard_private'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
