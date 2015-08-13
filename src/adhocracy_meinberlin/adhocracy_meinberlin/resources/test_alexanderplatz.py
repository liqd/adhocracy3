from pytest import mark
from pytest import fixture

class TestProcess:

    @fixture
    def meta(self):
        from .alexanderplatz import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.geo import ILocationReference
        from adhocracy_meinberlin import resources
        assert meta.iresource is resources.alexanderplatz.IProcess
        assert meta.extended_sheets == (ILocationReference,
                                        )
        assert meta.workflow_name == 'standard'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
