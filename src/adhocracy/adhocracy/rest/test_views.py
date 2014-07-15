"""Test rest.views module."""
import json
import unittest

from cornice.util import extract_json_data
from cornice.errors import Errors
from mock import patch
from pyramid import testing
import colander
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource


############
#  helper  #
############


class IResourceX(IResource):
    pass


class ISheetB(ISheet):
    pass


class CountSchema(colander.MappingSchema):

    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


class DummyFolder(testing.DummyResource):

    def add(self, name, resource, **kwargs):
        self[name] = resource
        resource.__parent__ = self
        resource.__name__ = name


class CorniceDummyRequest(testing.DummyRequest):

    def __init__(self, registry=None, **kw):
        class Dummy:
            pass

        self.headers = {}
        self.body = ''
        self.GET = {}
        self.POST = {}
        self.matchdict = {}
        self.validated = {}
        if registry is None:
            self.registry = Dummy()
        self.registry.cornice_deserializers = {'application/json': extract_json_data}
        self.content_type = 'application/json'
        self.errors = Errors(self)
        self.__dict__.update(kw)

    @property
    def json_body(self):
        return json.loads(self.body)



@patch('adhocracy.registry.ResourceContentRegistry')
def make_mock_resource_registry(mock_registry=None):
    return mock_registry.return_value


##########
#  tests #
##########


class ValidateRequestDataUnitTest(unittest.TestCase):

    def _make_one(self, context, request, **kw):
        from adhocracy.rest.views import validate_request_data
        validate_request_data(context, request, **kw)

    def setUp(self):
        self.request = CorniceDummyRequest()
        self.context = testing.DummyResource()
        setattr(self.request, 'errors', Errors(self.request))

    def test_valid_wrong_method_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self.request.method = 'wrong_method'
        self._make_one(self.context, self.request)
        assert self.request.validated == {}

    def test_valid_no_schema_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self._make_one(self.context, self.request)
        assert self.request.validated == {}

    def test_valid_with_schema_no_data(self):
        self.request.body = ''
        self._make_one(self.context, self.request, schema=CountSchema())
        assert self.request.validated == {}

    def test_valid_with_schema_no_data_empty_dict(self):
        schema = CountSchema
        self.request.body = '{}'
        self._make_one(schema, self.request)
        assert self.request.validated == {}

    def test_valid_with_schema_with_data(self):
        self.request.body = '{"count": "1"}'
        self._make_one(self.context, self.request, schema=CountSchema())
        assert self.request.validated == {'count': 1}

    def test_valid_with_schema_with_data_in_querystring(self):
        class QueryStringSchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        location='querystring')
        self.request.GET = {'count': 1}
        self._make_one(self.context, self.request, schema=QueryStringSchema())
        assert self.request.validated == {'count': 1}

    def test_non_valid_with_schema_wrong_data(self):
        from cornice.util import _JSONError
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(self.context, self.request, schema=CountSchema())
        assert self.request.errors != []

    def test_non_valid_with_schema_wrong_data_cleanup(self):
        from cornice.util import _JSONError
        self.request.validated == {'secret_data': 'buh'}
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(self.context, self.request, schema=CountSchema())
        assert self.request.validated == {}

    def test_valid_with_extra_validator(self):
        def validator1(context, request):
            request.validated = "validator1"

        self._make_one(self.context, self.request, extra_validators=[validator1])
        assert self.request.validated == "validator1"


class ValidatePOSTRootVersionsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        self.request = CorniceDummyRequest()

    def make_one(self, context, request):
        from adhocracy.rest.views import validate_post_root_versions
        validate_post_root_versions(context, request)

    def test_valid_no_value(self):
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_empty_value(self):
        self.make_one(self.context, self.request)
        self.request.validated = {'root_versions': []}
        assert self.request.errors == []

    def test_valid_with_value(self):
        from adhocracy.interfaces import IItemVersion
        from adhocracy.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IItemVersion, ISheet))
        self.context['root'] = root
        self.request.validated = {'root_versions': ["/root"]}

        self.make_one(self.context, self.request)

        assert self.request.errors == []
        assert self.request.validated == {'root_versions': [root]}

    def test_non_valid_value_has_wrong_iface(self):
        from adhocracy.interfaces import ISheet
        root = testing.DummyResource(__provides__=(IResourceX, ISheet))
        self.context['root'] = root
        self.request.validated = {'root_versions': ["/root"]}

        self.make_one(self.context, self.request)

        assert self.request.errors != []
        assert self.request.validated == {'root_versions': []}

    def test_non_valid_value_does_not_exists(self):
        self.request.validated = {'root_versions': ["/root"]}
        self.make_one(self.context, self.request)
        assert self.request.errors != []
        assert self.request.validated == {'root_versions': []}


class RESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder(__provides__=IResourceX)
        self.request = CorniceDummyRequest()
        resource_registry = object()
        self.request.registry.content = resource_registry

    def make_one(self, context, request):
        from adhocracy.rest.views import RESTView
        return RESTView(context, request)

    def test_create_valid(self):
        inst = self.make_one(self.context, self.request)
        assert inst.validation_GET == (None, [])
        assert inst.validation_HEAD == (None, [])
        assert inst.validation_OPTIONS == (None, [])
        assert inst.validation_PUT == (None, [])
        assert inst.validation_POST == (None, [])
        assert inst.reserved_names == []
        assert inst.context is self.context
        assert inst.request is self.request
        assert inst.request.errors == []
        assert inst.request.validated == {}
        assert inst.registry is self.request.registry.content


class ResourceRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder(__provides__=IResourceX)
        registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets
        self.resource_addables = request.registry.content.resource_addables

    def make_one(self, context, request):
        from adhocracy.rest.views import ResourceRESTView
        return ResourceRESTView(context, request)

    def test_create_valid(self, ):
        inst = self.make_one(self.context, self.request)
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)

    def test_options_valid_no_sheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.resource_sheets.return_value = {}
        self.resource_addables.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.options()

        wanted = OPTIONResourceResponseSchema().serialize()
        assert wanted == response

    def test_options_valid_with_sheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.resource_sheets.return_value = {'ipropertyx': object()}
        self.resource_addables.return_value = \
            {'iresourcex': {'sheets_mandatory': [],
                            'sheets_optional': ['ipropertyx']}}

        inst = self.make_one(self.context, self.request)
        response = inst.options()

        wanted = OPTIONResourceResponseSchema().serialize()
        wanted['PUT']['request_body'] = {'data': {'ipropertyx': {}}}
        wanted['GET']['response_body']['data']['ipropertyx'] = {}
        wanted['POST']['request_body'] = [{'content_type': 'iresourcex',
                                           'data': {'ipropertyx': {}}}]

        assert wanted == response

    def test_get_valid_no_sheets(self):
        from adhocracy.rest.schemas import GETResourceResponseSchema
        self.resource_sheets.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted['path'] = '/'
        wanted['data'] = {}
        wanted['content_type'] = IResourceX.__identifier__
        assert wanted == response

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_get_valid_with_sheets(self, dummy_sheet):
        sheet = dummy_sheet.return_value
        sheet.meta.isheet = ISheetB
        sheet.get_cstruct.return_value = 'dummy_cstruct'
        self.resource_sheets.return_value = {ISheetB.__identifier__: sheet}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        wanted = {ISheetB.__identifier__: 'dummy_cstruct'}
        assert wanted == response['data']


class SimpleRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder(__provides__=IResourceX)
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets

    def make_one(self, context, request):
        from adhocracy.rest.views import SimpleRESTView
        return SimpleRESTView(context, request)

    def test_create_valid(self, ):
        from adhocracy.rest.views import ResourceRESTView
        from adhocracy.rest.schemas import PUTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, ResourceRESTView)
        assert inst.validation_PUT == (PUTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_put_valid_no_sheets(self):
        self.resource_sheets.return_value = {}
        self.request.validated = {"content_type": "X", "data": {}}

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResourceX.__identifier__}
        assert wanted == response

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_put_valid_with_sheets(self, dummy_sheet=None):
        sheet = dummy_sheet.return_value
        self.resource_sheets.return_value = {ISheetB.__identifier__: sheet}
        data = {'content_type': 'X',
                'data': {ISheetB.__identifier__: {'x': 'y'}}}
        self.request.validated = data

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResourceX.__identifier__}
        assert wanted == response
        assert sheet.set.call_args[0][0] == {'x': 'y'}


class PoolRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder()
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.create = request.registry.content.create

    def make_one(self, context, request):
        from adhocracy.rest.views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create(self, ):
        from adhocracy.rest.views import SimpleRESTView
        from adhocracy.rest.schemas import POSTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTResourceRequestSchema, [])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_post_valid(self):
        child = testing.DummyResource(__provides__=IResourceX)
        child.__parent__ = self.context
        child.__name__ = 'child'
        self.create.return_value = child
        self.request.validated = {'content_type': IResourceX.__identifier__,
                                  'data': {}}
        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child', 'content_type': IResourceX.__identifier__}
        assert wanted == response


class ItemRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder()
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.create = request.registry.content.create

    def make_one(self, context, request):
        from adhocracy.rest.views import ItemRESTView
        return ItemRESTView(context, request)

    def test_create(self, ):
        from adhocracy.rest.views import validate_post_root_versions
        from adhocracy.rest.views import SimpleRESTView
        from adhocracy.rest.schemas import POSTItemRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == (POSTItemRequestSchema,
                                        [validate_post_root_versions])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_get_item_with_first_version(self):
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        context = testing.DummyResource(__provides__=IItem)
        context['first'] = testing.DummyResource(__provides__=IItemVersion)

        inst = self.make_one(context, self.request)

        wanted = {'path': '/', 'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/first'}
        assert inst.get() == wanted

    def test_get_item_without_first_version(self):
        from adhocracy.interfaces import IItem
        context = testing.DummyResource(__provides__=IItem)
        context['non_first'] = testing.DummyResource()

        inst = self.make_one(context, self.request)

        wanted = {'path': '/', 'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': ''}
        assert inst.get() == wanted

    def test_post_valid(self):
        child = testing.DummyResource(__provides__=IResourceX,
                                      __parent__=self.context,
                                      __name__='child')
        self.create.return_value = child
        self.request.validated = {'content_type': IResourceX.__identifier__,
                                  'data': {}}
        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child', 'content_type': IResourceX.__identifier__}
        self.create.assert_called_with(IResourceX.__identifier__, self.context,
                                       appstructs={}, root_versions=[])
        assert wanted == response

    def test_post_valid_item(self):
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        child = testing.DummyResource(__provides__=IItem,
                                      __parent__=self.context,
                                      __name__='child')
        first = testing.DummyResource(__provides__=IItemVersion)
        child['first'] = first
        self.create.return_value = child
        self.request.validated = {'content_type': IItemVersion.__identifier__,
                                  'data': {}}
        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child',
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/child/first'}
        assert wanted == response

    def test_post_valid_itemversion(self):
        from adhocracy.interfaces import IItemVersion
        child = testing.DummyResource(__provides__=IItemVersion,
                                      __parent__=self.context,
                                      __name__='child')
        root = testing.DummyResource(__provides__=IItemVersion)
        self.create.return_value = child
        self.request.validated = {'content_type':
                                      IItemVersion.__identifier__,
                                  'data': {},
                                  'root_versions': [root]}
        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child',
                  'content_type': IItemVersion.__identifier__}
        assert self.create.call_args[1]['root_versions'] == [root]
        assert wanted == response


class MetaApiViewUnitTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import resource_metadata
        from adhocracy.interfaces import sheet_metadata
        self.context = DummyFolder()
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.resources_metadata = request.registry.content.resources_metadata
        self.sheets_metadata = request.registry.content.sheets_metadata
        self.resource_meta = resource_metadata._replace(iresource=IResource)
        self.sheet_meta = sheet_metadata._replace(
            isheet=ISheet,
            schema_class=colander.MappingSchema)

    def make_one(self):
        from adhocracy.rest.views import MetaApiView
        return MetaApiView(self.context, self.request)

    def test_get_empty(self):
        self.resources_metadata.return_value = {}
        inst = self.make_one()

        response = inst.get()

        assert sorted(response.keys()) == ['resources', 'sheets']
        assert response['resources'] == {}
        assert response['sheets'] == {}

    def test_get_resources(self):
        metas = {IResource.__identifier__: self.resource_meta}
        self.resources_metadata.return_value = metas
        inst = self.make_one()
        resp = inst.get()
        assert IResource.__identifier__ in resp['resources']
        assert resp['resources'][IResource.__identifier__] == {'sheets': []}

    def test_get_resources_with_sheets_metadata(self):
        metas = {IResource.__identifier__: self.resource_meta._replace(
            basic_sheets=[ISheet],
            extended_sheets=[ISheetB])}
        self.resources_metadata.return_value = metas
        inst = self.make_one()

        resp = inst.get()['resources']

        wanted_sheets = [ISheet.__identifier__, ISheetB.__identifier__]
        assert wanted_sheets == resp[IResource.__identifier__]['sheets']

    def test_get_resources_with_element_types_metadata(self):
        metas = {IResource.__identifier__: self.resource_meta._replace(
            element_types=[IResource, IResourceX])}
        self.resources_metadata.return_value = metas
        inst = self.make_one()

        resp = inst.get()['resources']

        wanted = [IResource.__identifier__, IResourceX.__identifier__]
        assert wanted == resp[IResource.__identifier__]['element_types']

    def test_get_resources_with_item_type_metadata(self):
        metas = {IResource.__identifier__: self.resource_meta._replace(
            item_type=IResourceX)}
        self.resources_metadata.return_value = metas
        inst = self.make_one()

        resp = inst.get()['resources']

        wanted = IResourceX.__identifier__
        assert wanted == resp[IResource.__identifier__]['item_type']

    def test_get_sheets(self):
        sheets_meta = {ISheet.__identifier__: self.sheet_meta}
        self.sheets_metadata.return_value = sheets_meta
        inst = self.make_one()
        response = inst.get()
        assert ISheet.__identifier__ in response['sheets']
        assert 'fields' in response['sheets'][ISheet.__identifier__]
        assert response['sheets'][ISheet.__identifier__]['fields'] == []

    def test_get_sheets_with_field(self):
        class SchemaF(self.sheet_meta.schema_class):
            test = colander.SchemaNode(colander.Int())

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][ISheet.__identifier__]

        assert len(response['fields']) == 1
        field_metadata = response['fields'][0]
        assert field_metadata['create_mandatory'] is False
        assert field_metadata['readable'] is True
        assert field_metadata['editable'] is True
        assert field_metadata['creatable'] is True
        assert field_metadata['name'] == 'test'
        assert 'valuetype' in field_metadata

    def test_get_sheet_with_readonly_field(self):
        class SchemaF(self.sheet_meta.schema_class):
            test = colander.SchemaNode(colander.Int(), readonly=True)

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert field_metadata['editable'] is False
        assert field_metadata['creatable'] is False
        assert field_metadata['create_mandatory'] is False

    def test_get_sheets_with_field_colander_noniteratable(self):
        class SchemaF(self.sheet_meta.schema_class):
            test = colander.SchemaNode(colander.Int())

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'Integer'

    def test_get_sheets_with_field_adhocracy_noniteratable(self):
        from adhocracy.schema import Name

        class SchemaF(self.sheet_meta.schema_class):
            test = colander.SchemaNode(Name())

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'adhocracy.schema.Name'

    def test_get_sheets_with_field_adhocracy_referencelist(self):
        from adhocracy.interfaces import SheetToSheet
        from adhocracy.schema import ListOfUniqueReferences

        class SchemaF(self.sheet_meta.schema_class):
            test = ListOfUniqueReferences(reftype=SheetToSheet)

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        sheet_metadata = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = sheet_metadata['fields'][0]
        assert field_metadata['containertype'] == 'list'
        assert field_metadata['valuetype'] == 'adhocracy.schema.AbsolutePath'


class ValidateRequestDataDecoratorUnitTest(unittest.TestCase):

    def setUp(self):
        request = CorniceDummyRequest(method='get')
        request.registry.content = make_mock_resource_registry()
        self.request = request
        self.context = testing.DummyResource()

    def _make_dummy_view_class_with_decorator(self, validation_get=(None, [])):
        from adhocracy.rest.views import validate_request_data_decorator

        class DummyOriginalView:
            validation_GET = validation_get

        @validate_request_data_decorator()
        class DummyView(testing.DummyResource):
            __original_view__ = DummyOriginalView

        return DummyView

    def test_view_without_validators(self):
        view_class = self._make_dummy_view_class_with_decorator(
            validation_get=(None, []))

        view_class(self.context, self.request)

        assert self.request.validated == {}

    def test_view_with_validate_method(self):
        def dummy_validate(context, request):
            request.validated = {'data': True}
        view_class = self._make_dummy_view_class_with_decorator(
            validation_get=(None, [dummy_validate]))

        view_class(self.context, self.request)

        assert self.request.validated == {'data': True}

    def test_view_with_schema(self):
        view_class = self._make_dummy_view_class_with_decorator(
            validation_get=(CountSchema, []))
        self.request.body = '{"count":"1"}'

        view_class(self.context, self.request)

        assert self.request.validated == {'count': 1}
