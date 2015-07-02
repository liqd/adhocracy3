from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
from unittest.mock import Mock


class TestHasLogbookPoolSheet:

    @fixture
    def meta(self):
        from .logbook import has_logbook_pool_meta
        return has_logbook_pool_meta

    @fixture
    def inst(self, pool, service, meta):
        pool['logbook'] = service
        return meta.sheet_class(meta, pool)

    def test_meta(self, meta):
        from . import logbook
        assert meta.isheet == logbook.IHasLogbookPool
        assert meta.schema_class == logbook.HasLogbookPoolSchema
        assert meta.editable is False
        assert meta.creatable is False

    def test_get_empty(self, inst, service ):
        assert inst.get() == {'logbook_pool': service}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)

