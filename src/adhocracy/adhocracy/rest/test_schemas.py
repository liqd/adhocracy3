import unittest
import json
from mock import patch

from pyramid.testing import DummyResource
from pyramid.testing import DummyRequest
import colander
import pytest

from adhocracy.interfaces import ISheet


class ISheetA(ISheet):
    pass


class JSONDummyRequest(DummyRequest):

    @property
    def json_body(self):
        return json.loads(self.body)


class ResourceResponseSchemaUnitTest(unittest.TestCase):

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


class ItemResponseSchemaUnitTest(unittest.TestCase):

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


class POSTResourceRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.rest.schemas import POSTResourceRequestSchema
        return POSTResourceRequestSchema()

    def test_deserialize_missing_all(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})

    def test_deserialize_missing_contenttype(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'data': {}})

    def test_deserialize_with_data_and_contenttype(self):
        inst = self.make_one()
        data = {'content_type': 'VALID', 'data': {}}
        assert inst.deserialize(data) == data

    def test_deserialize_missing_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'content_type': 'VALID'})

    def test_deserialize_wrong_data_type(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'content_type': 'VALID', 'data': ""})

    def test_data_has_after_bind(self):
        from adhocracy.rest.schemas import add_post_data_subschemas
        inst = self.make_one()
        assert inst['data'].after_bind is add_post_data_subschemas

    def test_content_type_has_deferred_validator(self):
        from adhocracy.rest.schemas import deferred_validate_post_content_type
        inst = self.make_one()
        assert inst['content_type'].validator is deferred_validate_post_content_type


class DeferredValidatePostContentTypeUnitTest(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, mock_registry=None):
        request = DummyRequest()
        request.registry.content = mock_registry.return_value
        self.resource_addables = request.registry.content.resource_addables
        context = DummyResource()
        self.context_and_request_dict = {'context': context, 'request': request}
        self.node = colander.MappingSchema()

    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import deferred_validate_post_content_type
        return deferred_validate_post_content_type(node, kw)

    def test_without_content_types(self):
        self.resource_addables.return_value = {}
        validator = self._call_fut(self.node, self.context_and_request_dict)
        assert list(validator.choices) == []

    def test_with_content_types(self):
        self.resource_addables.return_value = {'type': {}}
        validator = self._call_fut(self.node, self.context_and_request_dict)
        assert list(validator.choices) == ['type']


class AddPostRequestSubSchemasUnitTest(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, mock_registry=None):
        from adhocracy.interfaces import sheet_metadata
        request = JSONDummyRequest(body='{}')
        request.registry.content = mock_registry.return_value
        self.request = request
        self.resource_addables = request.registry.content.resource_addables
        request.registry.content.sheets_metadata.return_value = \
            {ISheet.__identifier__: sheet_metadata._replace(isheet=ISheet,
                                                            schema_class=colander.MappingSchema),
             ISheetA.__identifier__: sheet_metadata._replace(isheet=ISheetA,
                                                             schema_class=colander.MappingSchema)}
        self.sheets_metadata = request.registry.content.sheets_metadata
        context = DummyResource()
        self.context_and_request_dict = {'context': context, 'request': request}
        self.node = colander.MappingSchema()

    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import add_post_data_subschemas
        return add_post_data_subschemas(node, kw)

    def test_no_data_and_no_sheets(self):
        self._call_fut(self.node, self.context_and_request_dict)
        assert self.node.children == []

    def test_no_data_and_optional_sheets(self):
        self.resource_addables.return_value = \
            {'VALID': {'sheets_mandatory': [],
                       'sheets_optional': [ISheet.__identifier__]}}

        self._call_fut(self.node, self.context_and_request_dict)

        assert self.node.children == []

    def test_data_and_optional_sheets(self):
        self.resource_addables.return_value = \
            {'VALID': {'sheets_mandatory': [],
                       'sheets_optional': [ISheet.__identifier__]}}
        data = {'content_type': 'VALID', 'data': {ISheet.__identifier__: {}}}
        self.request.body = json.dumps(data)

        self._call_fut(self.node, self.context_and_request_dict)

        assert len(self.node.children) == 1
        assert self.node.children[0].name == ISheet.__identifier__

    def test_data_and_mandatory_but_no_optional_sheets(self):
        self.resource_addables.return_value = \
            {'VALID': {'sheets_mandatory': [ISheetA.__identifier__],
                       'sheets_optional': [ISheet.__identifier__]}}
        data = {'content_type': 'VALID', 'data': {ISheetA.__identifier__: {}}}
        self.request.body = json.dumps(data)

        self._call_fut(self.node, self.context_and_request_dict)

        assert len(self.node.children) == 1
        assert self.node.children[0].name == ISheetA.__identifier__


class POSTItemRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.rest.schemas import POSTItemRequestSchema
        return POSTItemRequestSchema()

    def test_deserialize_without_root_versions(self):
        inst = self.make_one()
        result = inst.deserialize({'content_type': 'VALID', 'data': {}})
        assert 'root_versions' in result
        assert result['root_versions'] == []

    def test_deserialize_with_root_versions(self):
        inst = self.make_one()
        assert inst.deserialize({'content_type': "VALID", 'data': {},
                                 'root_versions': ["/path"]})

    def test_deserialize_with_root_versions_but_wrong_type(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({'content_type': "VALID", 'data': {},
                              'root_versions': ["?path"]})


class PUTResourceRequestSchemaUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.rest.schemas import PUTResourceRequestSchema
        return PUTResourceRequestSchema()

    def test_deserialize_with_data(self):
        inst = self.make_one()
        data = {'data': {}}
        assert inst.deserialize(data) == data

    def test_deserialize_missing_data(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.deserialize({})

    def test_data_has_after_bind(self):
        from adhocracy.rest.schemas import add_put_data_subschemas
        inst = self.make_one()
        assert inst['data'].after_bind is add_put_data_subschemas


class AddPutRequestSubSchemasUnitTest(unittest.TestCase):

    @patch('adhocracy.registry.ResourceContentRegistry')
    def setUp(self, mock_registry=None):
        from adhocracy.interfaces import sheet_metadata
        request = JSONDummyRequest(body='{}')
        request.registry.content = mock_registry.return_value
        self.request = request
        request.registry.content.sheets_metadata.return_value = \
            {ISheet.__identifier__: sheet_metadata._replace(isheet=ISheet,
                                                            schema_class=colander.MappingSchema),
             ISheetA.__identifier__: sheet_metadata._replace(isheet=ISheetA,
                                                             schema_class=colander.MappingSchema)}
        self.sheets_metadata = request.registry.content.sheets_metadata
        self.resource_sheets = request.registry.content.resource_sheets
        context = DummyResource()
        self.context_and_request_dict = {'context': context, 'request': request}
        self.node = colander.MappingSchema()

    def _call_fut(self, node, kw):
        from adhocracy.rest.schemas import add_put_data_subschemas
        return add_put_data_subschemas(node, kw)

    def test_no_data_and_no_sheets(self):
        self._call_fut(self.node, self.context_and_request_dict)
        assert self.node.children == []

    def test_no_data_and_optional_sheets(self):
        self.resource_sheets.return_value = {ISheet.__identifier__: None}
        self._call_fut(self.node, self.context_and_request_dict)
        assert self.node.children == []

    def test_data_and_optional_sheets(self):
        self.resource_sheets.return_value = {ISheet.__identifier__: None}
        self.request.body = json.dumps({'data': {ISheet.__identifier__: {}}})

        self._call_fut(self.node, self.context_and_request_dict)

        assert len(self.node.children) == 1
        assert self.node.children[0].name == ISheet.__identifier__
        assert self.node.children[0].bindings == self.context_and_request_dict


class OPTIONResourceResponseSchemaUnitTest(unittest.TestCase):

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
