from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark


class TestTagsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.tags import tags_meta
        return tags_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.tags import ITags
        from adhocracy_core.sheets.tags import TagsSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITags
        assert inst.meta.schema_class == TagsSchema
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'FIRST': None,
                              'LAST': None}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
