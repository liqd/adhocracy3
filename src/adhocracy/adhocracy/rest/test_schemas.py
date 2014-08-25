import json

from pyramid import testing
from pytest import fixture
from pytest import raises
import colander

from adhocracy.interfaces import ISheet


class ISheetA(ISheet):
    pass


class JSONDummyRequest(testing.DummyRequest):

    @property
    def json_body(self):
        return json.loads(self.body)



@fixture
def sheet_metas():
    from adhocracy.interfaces import sheet_metadata
    meta = sheet_metadata._replace(schema_class=colander.MappingSchema)
    metas = {ISheet.__identifier__: meta._replace(isheet=ISheet),
             ISheetA.__identifier__: meta._replace(isheet=ISheet)}
    return metas


class TestResourceResponseSchema:

    def make_one(self):
        from adhocracy.rest.schemas import ResourceResponseSchema
        return ResourceResponseSchema()

    def test_serialize_no_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': '', 'path': ''}
        assert inst.serialize() == wanted

    def test_serialize_with_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': 'x', 'path': '/'}
        assert inst.serialize({'content_type': 'x', 'path': '/'}) == wanted


class TestItemResponseSchema:

    def make_one(self):
        from adhocracy.rest.schemas import ItemResponseSchema
        return ItemResponseSchema()

    def test_serialize_no_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': '', 'path': '', 'first_version_path': ''}
        assert inst.serialize() == wanted

    def test_serialize_with_appstruct(self):
        inst = self.make_one()
        wanted = {'content_type': 'x', 'path': '/', 'first_version_path': '/v'}
        assert inst.serialize({'content_type': 'x', 'path': '/',
                               'first_version_path': '/v'}) == wanted


class TestPOSTResourceRequestSchema:

    def make_one(self):
        from adhocracy.rest.schemas import POSTResourceRequestSchema
        return POSTResourceRequestSchema()

    def test_deserialize_missing_all(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_missing_contenttype(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({'data': {}})

    def test_deserialize_with_data_and_contenttype(self):
        inst = self.make_one()
        data = {'content_type': 'VALID', 'data': {}}
        assert inst.deserialize(data) == data

    def test_deserialize_with_data_unknown(self):
        inst = self.make_one()
        data = {'content_type': 'VALID', 'data': {'unknown': 1}}
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_missing_data(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({'content_type': 'VALID'})

    def test_deserialize_wrong_data_type(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({'content_type': 'VALID', 'data': ""})

    def test_data_has_after_bind(self):
        from adhocracy.rest.schemas import add_post_data_subschemas
        inst = self.make_one()
        assert inst['data'].after_bind is add_post_data_subschemas

    def test_content_type_has_deferred_validator(self):
        from adhocracy.rest.schemas import deferred_validate_post_content_type
        inst = self.make_one()
        assert inst['content_type'].validator is deferred_validate_post_content_type


class TestDeferredValidatePostContentType:

    @fixture
    def request(self, mock_resource_registry):
        request = JSONDummyRequest()
        request.registry.content = mock_resource_registry
        return request

    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import deferred_validate_post_content_type
        return deferred_validate_post_content_type(node, kw)

    def test_without_content_types(self, node, request, context):
        validator = self._call_fut(node, {'context': context, 'request': request})
        assert list(validator.choices) == []

    def test_with_content_types(self, node, request, context):
        request.registry.content.resource_addables.return_value = {'type': {}}
        validator = self._call_fut(node, {'context': context, 'request': request})
        assert list(validator.choices) == ['type']


class TestAddPostRequestSubSchemas:

    @fixture
    def request(self, mock_resource_registry):
        request = JSONDummyRequest(body='{}')
        request.registry.content = mock_resource_registry
        return request


    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import add_post_data_subschemas
        return add_post_data_subschemas(node, kw)

    def test_no_data_and_no_sheets(self, node, request, context):
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children == []

    def test_no_data_and_optional_sheets(self, node, request, context, sheet_metas):
        request.registry.content.sheets_meta = sheet_metas
        request.registry.content.resource_addables.return_value =\
            {'VALID': {'sheets_mandatory': [],
                       'sheets_optional': [ISheet.__identifier__]}}
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children == []

    def test_data_and_optional_sheets(self, node, request, context, sheet_metas):
        request.registry.content.sheets_meta = sheet_metas
        request.registry.content.resource_addables.return_value =\
            {'VALID': {'sheets_mandatory': [],
                       'sheets_optional': [ISheet.__identifier__]}}
        data = {'content_type': 'VALID', 'data': {ISheet.__identifier__: {}}}
        request.body = json.dumps(data)
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children[0].name == ISheet.__identifier__

    def test_data_and_mandatory_but_no_optional_sheets(self, node, request, context, sheet_metas):
        request.registry.content.sheets_meta = sheet_metas
        request.registry.content.resource_addables.return_value =\
            {'VALID': {'sheets_mandatory': [ISheetA.__identifier__],
                       'sheets_optional': [ISheet.__identifier__]}}
        data = {'content_type': 'VALID', 'data': {ISheetA.__identifier__: {}}}
        request.body = json.dumps(data)
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children[0].name == ISheetA.__identifier__
        assert node.children[0].bindings == {'context': context, 'request': request}


class TestPOSTItemRequestSchemaUnitTest:

    def make_one(self):
        from adhocracy.rest.schemas import POSTItemRequestSchema
        return POSTItemRequestSchema()

    def test_deserialize_without_root_versions(self):
        inst = self.make_one()
        result = inst.deserialize({'content_type': 'VALID', 'data': {}})
        assert result == {'content_type': 'VALID', 'data': {},
                          'root_versions': []}

    def test_deserialize_with_root_versions(self):
        inst = self.make_one()
        result = inst.deserialize({'content_type': "VALID", 'data': {},
                                   'root_versions': ["/path"]})
        assert result == {'content_type': 'VALID', 'data': {},
                          'root_versions': ['/path']}

    def test_deserialize_with_root_versions_but_wrong_type(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({'content_type': "VALID", 'data': {},
                              'root_versions': ["?path"]})


class TestPUTResourceRequestSchema:

    def make_one(self):
        from adhocracy.rest.schemas import PUTResourceRequestSchema
        return PUTResourceRequestSchema()

    def test_deserialize_with_data(self):
        inst = self.make_one()
        data = {'data': {}}
        assert inst.deserialize(data) == data

    def test_deserialize_with_data_unknown(self):
        inst = self.make_one()
        data = {'data': {'unknown': 1}}
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_missing_data(self):
        inst = self.make_one()
        with raises(colander.Invalid):
            inst.deserialize({})

    def test_data_has_after_bind(self):
        from adhocracy.rest.schemas import add_put_data_subschemas
        inst = self.make_one()
        assert inst['data'].after_bind is add_put_data_subschemas


class TestAddPutRequestSubSchemasUnitTest:

    @fixture
    def request(self, mock_resource_registry):
        request = JSONDummyRequest(body='{}')
        request.registry.content = mock_resource_registry
        return request

    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import add_put_data_subschemas
        return add_put_data_subschemas(node, kw)

    def test_no_data_and_no_sheets(self, node, context, request):
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children == []

    def test_no_data_and_optional_sheets(self, node, context, request):
        request.registry.content.resource_sheets.return_value = {ISheet.__identifier__: None}
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children == []

    def test_data_and_optional_sheets(self, node, context, request, sheet_metas):
        request.registry.content.sheets_meta = sheet_metas
        request.registry.content.resource_sheets.return_value = {ISheet.__identifier__: None}
        request.body = json.dumps({'data': {ISheet.__identifier__: {}}})
        self._call_fut(node, {'context': context, 'request': request})
        assert node.children[0].name == ISheet.__identifier__
        assert node.children[0].bindings == {'context': context, 'request': request}


class TestOPTIONResourceResponseSchema:

    def make_one(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        return OPTIONResourceResponseSchema()

    def test_serialize_no_sheets_and_no_addables(self):
        inst = self.make_one()
        wanted =\
            {'GET': {'request_body': {},
                     'request_querystring': {},
                     'response_body': {'content_type': '', 'data': {},
                                       'path': ''}},
             'HEAD': {},
             'OPTION': {},
             'POST': {'request_body': [],
                      'response_body': {'content_type': '', 'path': ''}},
             'PUT': {'request_body': {'data': {}},
                     'response_body': {'content_type': '', 'path': ''}}}
        assert inst.serialize() == wanted


class TestPOSTBatchRequestItem:

    def make_one(self):
        from adhocracy.rest.schemas import POSTBatchRequestItem
        return POSTBatchRequestItem()

    def test_deserialize_valid(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        assert inst.deserialize(data) == data

    def test_deserialize_at_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '@par1_item',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        assert inst.deserialize(data) == data

    def test_deserialize_atat_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '@@par1_item',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        assert inst.deserialize(data) == data

    def test_deserialize_invalid_relative_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': 'par1_item',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_missing_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_invalid_method(self):
        inst = self.make_one()
        data = {
            'method': 'BRIEF',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'par1_item'
        }
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_invalid_body(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': 'This is not a JSON dict',
            'result_path': 'par1_item'
        }
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_empty_result_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': ''
        }
        assert inst.deserialize(data) == data

    def test_deserialize_no_result_path(self):
        """result_path defaults to an empty string."""
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'}
        }
        deserialized = inst.deserialize(data)
        assert deserialized['result_path'] == ''

    def test_deserialize_invalid_result_path(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'},
            'result_path': 'not an identifier'
        }
        with raises(colander.Invalid):
            inst.deserialize(data)


class TestPOSTBatchRequestSchema:

    def make_one(self):
        from adhocracy.rest.schemas import POSTBatchRequestSchema
        return POSTBatchRequestSchema()

    def test_deserialize_valid(self):
        inst = self.make_one()
        data = [{
                'method': 'POST',
                'path': '/adhocracy/Proposal/kommunismus',
                'body': {'content_type': 'adhocracy.resources.IParagraph'},
                'result_path': 'par1_item'
            },
            {
                'method': 'GET',
                'path': '@@par1_item'
            }
        ]
        data_with_defaults = data.copy()
        data_with_defaults[1]['body'] = {}
        data_with_defaults[1]['result_path'] = ''
        assert inst.deserialize(data) == data_with_defaults

    def test_deserialize_invalid_inner_field(self):
        inst = self.make_one()
        data = [{
                'method': 'POST',
                'path': '/adhocracy/Proposal/kommunismus',
                'body': {'content_type': 'adhocracy.resources.IParagraph'},
                'result_path': 'par1_item'
            },
            {
                'method': 'HOT',
                'path': '@@par1_item'
            }
        ]
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_invalid_inner_type(self):
        inst = self.make_one()
        data = [{
                'method': 'POST',
                'path': '/adhocracy/Proposal/kommunismus',
                'body': {'content_type': 'adhocracy.resources.IParagraph'},
                'result_path': 'par1_item'
            },
            ['this', 'is not', 'a dictionary']
        ]
        with raises(colander.Invalid):
            inst.deserialize(data)

    def test_deserialize_invalid_outer_type(self):
        inst = self.make_one()
        data = {
            'method': 'POST',
            'path': '/adhocracy/Proposal/kommunismus',
            'body': {'content_type': 'adhocracy.resources.IParagraph'}
        }
        with raises(colander.Invalid):
            inst.deserialize(data)
