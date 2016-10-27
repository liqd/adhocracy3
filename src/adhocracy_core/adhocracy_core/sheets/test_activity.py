from pyramid import testing
from pytest import fixture
from pytest import mark


class TestActivitySheet:

    @fixture
    def meta(self):
        from .activity import activity_meta
        return activity_meta

    @fixture
    def mock_now(self, monkeypatch):
        from adhocracy_core.utils import now
        date = now()
        monkeypatch.setattr('adhocracy_core.schema.now', lambda: date)
        return date

    def test_meta(self, meta):
        from adhocracy_core.sheets.activity import IActivity
        from adhocracy_core.sheets.activity import ActivitySchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        assert meta.sheet_class == AnnotationRessourceSheet
        assert meta.isheet == IActivity
        assert meta.schema_class == ActivitySchema
        assert meta.editable is False
        assert meta.creatable is True

    def test_create(self, meta, context):
        assert meta.sheet_class(meta, context, None)

    def test_get_empty(self, meta, context, mock_now):
        inst = meta.sheet_class(meta, context, None)
        assert inst.get() ==  {'name': '',
                               'object': None,
                               'published': mock_now,
                               'subject': None,
                               'target': None,
                               'type': ''}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
