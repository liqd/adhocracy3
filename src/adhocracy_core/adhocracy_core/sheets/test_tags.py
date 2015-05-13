from unittest.mock import Mock

from pyramid import testing
from pytest import fixture


class TestTagsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.tags import tags_meta
        return tags_meta

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
        from adhocracy_core.sheets.tags import tag_meta
        return tag_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.tags import ITag
        from adhocracy_core.sheets.tags import TagSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITag
        assert inst.meta.schema_class == TagSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'elements': []}


class TestFilterByTag:

    def _tag_names_to_tags(self, names: list) -> list:
        return [testing.DummyResource(__name__=name) for name in names]

    def _inject_mock_graph(self, monkeypatch, return_value):
        from adhocracy_core.sheets import tags
        mock_graph = Mock()
        mock_graph.get_back_reference_sources.return_value = return_value
        mock_find_graph = Mock(return_value=mock_graph)
        monkeypatch.setattr(tags, 'find_graph', mock_find_graph)

    def test_filter_by_tag_empty_list(self):
        from adhocracy_core.sheets.tags import filter_by_tag
        assert filter_by_tag([], 'mytag') == []

    def test_filter_by_tag_has_tag(self, monkeypatch, context):
        from adhocracy_core.sheets.tags import filter_by_tag
        self._inject_mock_graph(monkeypatch,
                                self._tag_names_to_tags(['mytag']))
        assert filter_by_tag([context], 'mytag') == [context]

    def test_filter_by_tag_has_another_tag(self, monkeypatch, context):
        from adhocracy_core.sheets.tags import filter_by_tag
        self._inject_mock_graph(monkeypatch,
                                self._tag_names_to_tags(['thistag']))
        assert filter_by_tag([context], 'thattag') == []

    def test_filter_by_tag_has_seveal_tag(self, monkeypatch, context):
        from adhocracy_core.sheets.tags import filter_by_tag
        self._inject_mock_graph(monkeypatch, self._tag_names_to_tags(
            ['thistag', 'thattag']))
        assert filter_by_tag([context], 'thattag') == [context]


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
