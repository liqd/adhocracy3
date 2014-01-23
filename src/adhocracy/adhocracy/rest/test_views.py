"""Test rest.views module."""
from adhocracy.properties.interfaces import IProperty
from adhocracy.resources.interfaces import IResource
from cornice.util import (
    extract_json_data,
)
from cornice.errors import Errors
from mock import patch
from pyramid import testing
from zope.interface import (
    taggedValue,
)
from zope.dottedname.resolve import resolve

import colander
import pytest
import unittest


############
#  helper  #
############

class IResourceX(IResource):
    pass


class IPropertyB(IProperty):
    taggedValue('schema', 'adhocracy.rest.test_views.CountSchema')


class CountSchema(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


class Dummy(object):
    pass


class DummyFolder(testing.DummyResource):

    def add(self, name, resource, **kwargs):
        self[name] = resource

    def next_name(self, *kwargs):
        return '0000001'

    def check_name(self, name, reserved_names=[]):
        return name


class CorniceDummyRequest(testing.DummyRequest):

    def __init__(self, registry=None):
        self.headers = {}
        self.body = ''
        self.GET = {}
        self.POST = {}
        self.matchdict = {}
        self.validated = {}
        if registry is None:
            self.registry = Dummy()
        self.registry.cornice_deserializers = {'application/json':
                                               extract_json_data}
        self.content_type = 'application/json'
        self.errors = Errors(self)


@patch('adhocracy.registry.ResourceContentRegistry', autospec=True)
def make_mock_resource_registry(mock_registry=None):
    return mock_registry.return_value


@patch('adhocracy.registry.ResourceContentRegistry', autospec=True)
def make_mock_resource_registry_with_mock_type(iresource, mock_registry=None):
    registry = mock_registry.return_value
    registry.typeof.return_value = iresource.__identifier__
    return registry


@patch('adhocracy.properties.ResourcePropertySheetAdapter')
def make_mock_sheet(iproperty, dummy_sheet=None):
    sheet = dummy_sheet.return_value
    sheet.iface = iproperty
    schema = resolve(iproperty.getTaggedValue('schema'))
    sheet.schema = schema()
    cstruct = sheet.schema.serialize()
    sheet.get_cstruct.return_value = cstruct
    sheet.permission_view = 'view'
    sheet.permission_edit = 'edit'
    sheet.readonly = False
    sheet.createmandatory = False
    return sheet


class DummyPropertysheet(Dummy):
    readonly = False
    createmandatory = False


##########
#  tests #
##########

class ValidateRequestDataUnitTest(unittest.TestCase):

    def make_one(self, context, request, **kw):
        from .views import validate_request_data
        validate_request_data(context, request, **kw)

    def setUp(self):
        self.config = testing.setUp()
        self.request = CorniceDummyRequest()
        self.context = testing.DummyResource()
        setattr(self.request, 'errors', Errors(self.request))

    def test_valid_wrong_method_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self.request.method = 'wrong_method'
        self.make_one(self.context, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_no_schema_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self.make_one(self.context, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_no_data(self):
        schema = CountSchema
        self.request.body = ''
        self.make_one(self.context, self.request, schema=schema)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_no_data_empty_dict(self):
        schema = CountSchema
        self.request.body = '{}'
        self.make_one(schema, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_with_data(self):
        schema = CountSchema
        self.request.body = '{"count": "1"}'
        self.make_one(self.context, self.request, schema=schema)
        wanted = {'count': 1}
        assert self.request.validated == wanted

    def test_non_valid_with_schema_wrong_data(self):
        from cornice.util import _JSONError
        schema = CountSchema
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self.make_one(schema, self.request, schema=schema)
        assert self.request.errors != []

    def test_non_valid_with_schema_wrong_data_cleanup(self):
        from cornice.util import _JSONError
        schema = CountSchema
        self.request.validated == {'secret_data': 'buh'}
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self.make_one(schema, self.request, schema=schema)
        assert self.request.validated == {}

    def test_valid_with_extra_validator(self):
        schema = CountSchema

        def validator1(context, request):
            request.validated = "validator1"

        self.make_one(schema, self.request, extra_validators=[validator1])
        assert self.request.validated == "validator1"


class ValidatePUTPropertysheetNamesUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = testing.DummyResource()
        request = CorniceDummyRequest(registry=self.config.registry)
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request

    def make_one(self, context, request):
        from .views import validate_put_sheet_names
        validate_put_sheet_names(context, request)

    def test_valid_no_sheets(self):
        sheets = self.request.registry.content.resource_sheets
        sheets.return_value = {}
        self.request.validated = {'data': {}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_with_sheets(self):
        self.request.registry.content.resource_sheets.return_value =\
            {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)

        self.request.registry.content.resource_sheets.assert_called_with(
            self.context, self.request, onlyeditable=True)
        assert self.request.errors == []

    def test_valid_with_sheets_missing(self):
        self.request.registry.content.resource_sheets.return_value =\
            {'sheet': DummyPropertysheet(), 'sheetB': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_with_sheets_missing_createmandatory(self):
        sheets = {'sheet': DummyPropertysheet(),
                  'sheetB': DummyPropertysheet()}
        sheets['sheetB'].createmandatory = True
        self.request.registry.content.resource_sheets.return_value =\
            sheets
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_non_valid_with_sheets_wrong_name(self):
        self.request.registry.content.resource_sheets.return_value =\
            {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'wrongname': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors != []


class ValidatePOSTPropertysheetNamesAddablesUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = testing.DummyResource()
        request = CorniceDummyRequest(registry=self.config.registry)
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request

    def make_one(self, context, request):
        from .views import validate_post_sheet_names_and_resource_type
        validate_post_sheet_names_and_resource_type(context, request)

    def test_valid_optional(self):
        registry = self.request.registry.content
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_mandatory': [],
            'sheets_optional': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors == []

    def test_valid_mandatory(self):
        registry = self.request.registry.content
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors == []

    def test_non_valid_wrong_content_type(self):
        registry = self.request.registry.content
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'wrong_iresource',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_wrong_sheet(self):
        registry = self.request.registry.content
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'wrong_iproperty': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_missing_sheet_mandatory(self):
        registry = self.request.registry.content
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': ['propertyy'],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyy': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []


class RESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = DummyFolder(__provides__=IResourceX)
        self.request = CorniceDummyRequest(registry=self.config.registry)
        registry = None
        self.request.registry.content = registry
        self.request.errors = Errors(self.request)

    def tearDown(self):
        testing.tearDown()

    def make_one(self, context, request):
        from .views import RESTView
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
        self.config = testing.setUp()
        self.context = DummyFolder(__provides__=IResourceX)
        registry = make_mock_resource_registry_with_mock_type(IResourceX)
        self.request = CorniceDummyRequest(registry=self.config.registry)
        self.request.registry.content = registry
        self.request.errors = Errors(self.request)

    def tearDown(self):
        testing.tearDown()

    def make_one(self, context, request):
        from .views import ResourceRESTView
        return ResourceRESTView(context, request)

    def test_create_valid(self,):
        inst = self.make_one(self.context, self.request)
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)

    def test_options_valid_no_sheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.request.registry.content.resource_sheets.return_value = {}
        self.request.registry.content.resource_addables.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.options()

        wanted = OPTIONResourceResponseSchema().serialize()
        assert wanted == response

    def test_options_valid_with_sheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.request.registry.content.resource_sheets.return_value = {
            'ipropertyx': Dummy()}
        self.request.registry.content.resource_addables.return_value = {
            'iresourcex': {'sheets_mandatory': [],
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
        self.request.registry.content.resource_sheets.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted['path'] = '/'
        wanted['data'] = {}
        wanted['content_type'] = IResourceX.__identifier__
        assert wanted == response

    def test_get_valid_with_sheets(self):
        sheet = make_mock_sheet(IPropertyB)
        self.request.registry.content.resource_sheets.return_value = {
            IPropertyB.__identifier__: sheet}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        data = sheet.schema.serialize()
        wanted = {IPropertyB.__identifier__: data}
        assert wanted == response['data']


class FubelRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = DummyFolder(__provides__=IResourceX)
        registry = make_mock_resource_registry_with_mock_type(IResourceX)
        self.request = CorniceDummyRequest(registry=self.config.registry)
        self.request.registry.content = registry
        self.request.errors = Errors(self.request)

    def tearDown(self):
        testing.tearDown()

    def make_one(self, context, request):
        from .views import FubelRESTView
        return FubelRESTView(context, request)

    def test_create_valid(self,):
        from .views import validate_put_sheet_names
        from .schemas import PUTResourceRequestSchema
        from .views import ResourceRESTView
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, ResourceRESTView)
        assert inst.validation_PUT == (PUTResourceRequestSchema,
                                       [validate_put_sheet_names])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_put_valid_no_sheets(self):
        self.request.registry.content.resource_sheets.return_value = {}
        self.request.validated = {"content_type": "X", "data": {}}

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResourceX.__identifier__}
        assert wanted == response

    def test_put_valid_with_sheets(self):
        sheet = make_mock_sheet(IPropertyB)
        sheet.set_cstruct.return_value = True
        self.request.registry.content.resource_sheets.return_value = {
            IPropertyB.__identifier__: sheet}
        data = {'content_type': IResource.__identifier__,
                'data': {IPropertyB.__identifier__: {'x': 'y'}}}
        self.request.validated = data

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResourceX.__identifier__}
        assert wanted == response
        assert sheet.set_cstruct.called

    def test_put_non_valid_with_sheets_raise_invalid(self):
        sheet = make_mock_sheet(IPropertyB)
        self.request.registry.content.resource_sheets.return_value = {
            IPropertyB.__identifier__: sheet}
        data = {'content_type': IResource.__identifier__,
                'data': {IPropertyB.__identifier__: {'x': 'y'}}}
        self.request.validated = data

        invalid_node = colander.SchemaNode(typ=colander.String())
        sheet.set_cstruct.side_effect = colander.Invalid(invalid_node)

        inst = self.make_one(self.context, self.request)
        with pytest.raises(colander.Invalid):
            inst.put()


class PoolRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = DummyFolder(__provides__=IResourceX)
        registry = make_mock_resource_registry_with_mock_type(IResourceX)
        self.request = CorniceDummyRequest(registry=self.config.registry)
        self.request.registry.content = registry
        self.request.errors = Errors(self.request)

    def tearDown(self):
        testing.tearDown()

    def make_one(self, context, request):
        from .views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create_valid(self,):
        from .views import validate_post_sheet_names_and_resource_type
        from .schemas import POSTResourceRequestSchema
        from .views import FubelRESTView
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, FubelRESTView)
        assert inst.validation_POST ==\
            (POSTResourceRequestSchema,
             [validate_post_sheet_names_and_resource_type])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_post_valid_with_sheets(self):
        from adhocracy.properties.interfaces import IName
        sheet = make_mock_sheet(IPropertyB)
        sheet.set_cstruct.return_value = True
        registry = self.request.registry.content
        registry.create.return_value = testing.DummyResource()
        registry.resource_sheets.return_value =\
            {IName.__identifier__: sheet}
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_mandatory': [],
            'sheets_optional': [IName.__identifier__]}}
        data = {'content_type': 'iresourcex',
                'data': {IName.__identifier__: {'name': 'child'}}}
        self.request.validated = data

        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child', 'content_type': IResourceX.__identifier__}
        assert wanted == response
        assert 'child' in self.context

    def test_post_non_valid_with_sheets_raise_invalid(self):
        sheet = make_mock_sheet(IPropertyB)
        sheet.set_cstruct.return_value = True
        invalid_node = colander.SchemaNode(typ=colander.String())
        sheet.set_cstruct.side_effect = colander.Invalid(invalid_node)
        registry = self.request.registry.content
        registry.create.return_value = testing.DummyResource()
        registry.resource_sheets.return_value = {'ipropertyx': sheet}
        registry.resource_addables.return_value = {'iresourcex': {
            'sheets_mandatory': [],
            'sheets_optional': ['ipropertyx']}}
        data = {"content_type": "iresourcex",
                "data": {"ipropertyx": {"a": "b"}}}
        self.request.validated = data

        inst = self.make_one(self.context, self.request)
        with pytest.raises(colander.Invalid):
            inst.post()
