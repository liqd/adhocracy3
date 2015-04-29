from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest.mock import Mock


@fixture
def mock_metadata_sheet(context, mock_sheet, registry_with_content):
    from adhocracy_core.testing import register_sheet
    from .metadata import IMetadata
    mock_sheet.meta = mock_sheet.meta._replace(isheet=IMetadata)
    register_sheet(context, mock_sheet, registry_with_content)
    return mock_sheet


class TestIMetadataSchema:

    @fixture
    def request_(self):
        return testing.DummyRequest()

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

    def test_serialize_empty(self):
        from colander import null
        inst = self.make_one()
        result = inst.serialize({})
        assert result['creation_date'] == null
        assert result['creator'] == ''
        assert result['item_creation_date'] == null
        assert result['modification_date'] == null
        assert result['modified_by'] == ''
        assert result['deleted'] == 'false'
        assert result['hidden'] == 'false'

    def test_serialize_empty_and_bind(self, context, mock_now):
        inst = self.make_one().bind(context=context)
        result = inst.serialize({})
        now_str = mock_now.isoformat()
        assert result['creation_date'] == now_str
        assert result['item_creation_date'] == now_str
        assert result['modification_date'] == now_str

    def test_deserialize_hiding_requires_permission(self, context, request_):
        import colander
        inst = self.make_one().bind(context=context, request=request_)
        request_.has_permission = Mock(return_value=False)
        with raises(colander.Invalid):
            inst.deserialize({'hidden': False})
        request_.has_permission = Mock(return_value=True)
        result = inst.deserialize({'hidden': False})
        assert result['hidden'] is False

    def test_deserialize_delete_doesnt_require_permission(self, context, request_):
        inst = self.make_one().bind(context=context, request=request_)
        request_.has_permission = Mock(return_value=True)
        result = inst.deserialize({'deleted': False})
        assert result['deleted'] is False


class TestMetadataSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.metadata import metadata_meta
        return metadata_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.sheets.metadata import MetadataSchema
        from . import AttributeStorageSheet
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IMetadata
        assert inst.meta.schema_class == MetadataSchema
        assert inst.meta.editable is True
        assert inst.meta.creatable is True
        assert inst.meta.readable is True
        assert inst.meta.sheet_class is AttributeStorageSheet



@fixture
def integration(config):
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.sheets.metadata')


@mark.usefixtures('integration')
def test_includeme_register_metadata_sheet(config):
    from adhocracy_core.sheets.metadata import IMetadata
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IMetadata)
    assert get_sheet(context, IMetadata)


class TestVisibility:

    @fixture
    def resource_with_metadata(self, integration):
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.sheets.metadata import IMetadata
        return testing.DummyResource(__provides__=[IResource, IMetadata])

    def test_view_blocked_by_metadata_no_imetadata(self, registry):
        from adhocracy_core.interfaces import IResource
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        resource = testing.DummyResource(__provides__=IResource)
        assert view_blocked_by_metadata(resource, registry, 'hidden') ==\
               {'reason': 'hidden'}

    def test_view_blocked_by_metadata_with_imetadata(
            self, pool_graph, resource_with_metadata, registry):
        from datetime import datetime
        from adhocracy_core.resources.principal import IUser
        from adhocracy_core.sheets.metadata import IMetadata
        from adhocracy_core.sheets.metadata import view_blocked_by_metadata
        from adhocracy_core.utils import get_sheet
        pool_graph['res'] = resource_with_metadata
        metadata = get_sheet(resource_with_metadata, IMetadata,
                             registry=registry)
        appstruct = metadata.get()
        user = testing.DummyRequest(__provides__=IUser)
        pool_graph['user'] = user
        now = datetime.now()
        appstruct['modified_by'] = user
        appstruct['modification_date'] = now
        metadata.set(appstruct, omit_readonly=False, send_event=False)
        resource_with_metadata.hidden = True
        result = view_blocked_by_metadata(resource_with_metadata, registry,
                                          'hidden')
        assert result['modified_by'] == user
        assert result['modification_date'] == now
