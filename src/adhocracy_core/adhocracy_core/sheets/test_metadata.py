from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest.mock import Mock


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestIMetadataSchema:

    @fixture
    def mock_now(self, monkeypatch):
        from adhocracy_core.utils import now
        date = now()
        monkeypatch.setattr('adhocracy_core.schema.now', lambda: date)
        return date

    def make_one(self, **kwargs):
        from adhocracy_core.sheets.metadata import MetadataSchema
        return MetadataSchema(**kwargs)

    def test_deserialize_empty(self):
        inst = self.make_one()
        result = inst.deserialize({})
        assert result == {'deleted': False, 'hidden': False}

    def test_deserialize_hiding_requires_permission(self, context, request_):
        import colander
        inst = self.make_one().bind(context=context, request=request_)
        request_.has_permission = Mock(return_value=False)
        with raises(colander.Invalid):
            inst.deserialize({'hidden': False})

    def test_serialize_empty(self):
        from colander import null
        inst = self.make_one()
        result = inst.serialize({})
        assert result['creation_date'] == null
        assert result['creator'] is None
        assert result['item_creation_date'] == null
        assert result['modification_date'] == null
        assert result['modified_by'] is None
        assert result['deleted'] == 'false'
        assert result['hidden'] == 'false'

    def test_serialize_empty_and_bind(self, context, mock_now, request_):
        inst = self.make_one().bind(context=context, request=request_)
        result = inst.serialize({})
        now_str = mock_now.isoformat()
        assert result['creation_date'] == now_str
        assert result['item_creation_date'] == now_str
        assert result['modification_date'] == now_str


class TestMetadataSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.metadata import metadata_meta
        return metadata_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.sheets.metadata import MetadataSchema
        from . import AttributeResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert inst.meta.isheet == IMetadata
        assert inst.meta.schema_class == MetadataSchema
        assert inst.meta.editable is True
        assert inst.meta.creatable is True
        assert inst.meta.readable is True
        assert inst.meta.sheet_class is AttributeResourceSheet

    @mark.usefixtures('integration')
    def test_includeme_register_sheet(self, meta, config):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert config.registry.content.get_sheet(context, meta.isheet)


class TestVisibility:

    def call_fut(self, *args):
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        return view_blocked_by_metadata(*args)

    def test_view_blocked_by_metadata_no_imetadata(self, registry):
        from adhocracy_core.interfaces import IResource
        resource = testing.DummyResource(__provides__=IResource)
        result = self.call_fut(resource, registry, 'hidden')
        assert result == {'reason':  'hidden'}

    def test_view_blocked_by_metadata_with_imetadata(self, registry, mock_sheet):
        from datetime import datetime
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.resources.principal import IUser
        resource = testing.DummyResource(__provides__=[IResource, IMetadata],
                                         hidden=True)
        user = testing.DummyResource(__provides__=IUser)
        now = datetime.now()
        mock_sheet.get.return_value = {'modified_by': user,
                                       'modification_date': now}
        registry.content.get_sheet.return_value = mock_sheet
        result = self.call_fut(resource, registry, 'hidden')
        assert result['modified_by'] == user
        assert result['modification_date'] == now


class TestIsOlderThen:

    def call_fut(self, *args):
        from .metadata import is_older_than
        return is_older_than(*args)

    @fixture
    def now(self):
        from pytz import UTC
        from datetime import datetime
        now = datetime.utcnow().replace(tzinfo=UTC)
        return now

    def test_creation_date_older_then_days(self, context, now):
        from datetime import timedelta
        context.creation_date = now - timedelta(days=8)
        assert self.call_fut(context, 7) is True

    def test_creation_date_equal_to_days(self, context, now):
        from datetime import timedelta
        context.creation_date = now - timedelta(days=7)
        assert self.call_fut(context, 7) is False

    def test_creation_date_younger_then_days(self, context, now):
        context.creation_date = now
        assert self.call_fut(context, 7) is False
