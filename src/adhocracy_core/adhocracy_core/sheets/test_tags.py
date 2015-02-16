from pyramid import testing
from pytest import fixture


class TestTagsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.tags import tags_metadata
        return tags_metadata

    def test_create(self, meta, context):
        from adhocracy_core.sheets.tags import ITags
        from adhocracy_core.sheets.tags import TagsSchema
        from adhocracy_core.sheets.pool import PoolSheet
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITags
        assert inst.meta.sheet_class == PoolSheet
        assert inst.meta.schema_class == TagsSchema
        assert inst.meta.editable is False
        assert inst.meta.creatable is False

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}

    def test_get_not_empty_with_target_isheet(self, meta, context):
        from adhocracy_core.sheets.tags import ITag
        child = testing.DummyResource(__provides__=ITag)
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': [child]}

    def test_get_not_empty_without_target_isheet(self, meta, context):
        child = testing.DummyResource()
        context['child1'] = child
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}


def test_includeme_register_tags_sheet(config):
    from adhocracy_core.sheets.tags import ITags
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.tags')
    context = testing.DummyResource(__provides__=ITags)
    assert get_sheet(context, ITags)


class TestTagSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.tags import tag_metadata
        return tag_metadata

    def test_create(self, meta, context):
        from adhocracy_core.sheets.tags import ITag
        from adhocracy_core.sheets.tags import TagSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITag
        assert inst.meta.schema_class == TagSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}


def test_includeme_register_tag_sheet(config):
    from adhocracy_core.sheets.tags import ITag
    from adhocracy_core.utils import get_sheet
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.tags')
    context = testing.DummyResource(__provides__=ITag)
    assert get_sheet(context, ITag)
