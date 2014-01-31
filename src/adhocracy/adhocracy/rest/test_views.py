"""Test rest.views module."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from cornice.util import extract_json_data
from cornice.errors import Errors
from mock import patch
from pyramid import testing
from zope.interface import taggedValue

import colander
import pytest
import unittest


############
#  helper  #
############

class IResourceX(IResource):
    pass


class ISheetB(ISheet):
    taggedValue('schema', 'adhocracy.rest.test_views.CountSchema')


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

    def __init__(self, registry=None):
        class Dummy(object):
            pass
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


class DummyPropertysheet(object):

    iface = None
    readonly = False
    createmandatory = False

    _dummy_appstruct = None

    def validate_cstruct(self, cstruct):
        if 'dummy_invalid' in cstruct:
            raise colander.Invalid(None)
        cstruct['dummy_validated'] = True
        return cstruct

    def get_cstruct(self):
        return {'dummy_cstruct': {}}

    def set(self, appstruct):
        self._dummy_appstruct = appstruct


##########
#  tests #
##########


class ValidateRequestDataUnitTest(unittest.TestCase):

    def make_one(self, context, request, **kw):
        from .views import validate_request_data
        validate_request_data(context, request, **kw)

    def setUp(self):
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


class ValidatePropertysheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        self.request = CorniceDummyRequest()

    def make_one(self, context, request, sheets):
        from .views import validate_sheet_cstructs
        validate_sheet_cstructs(context, request, sheets)

    def test_valid_no_sheets(self):
        sheets = {}
        self.request.validated = {'data': {}}
        self.make_one(self.context, self.request, sheets)
        assert self.request.validated == {'data': {}}

    def test_valid_no_sheets_no_data(self):
        sheets = {}
        self.request.validated = {}
        self.make_one(self.context, self.request, sheets)
        assert self.request.validated == {}

    def test_valid_with_sheets(self):
        sheets = {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request, sheets)
        assert self.request.validated['data']['sheet']['dummy_validated']

    def test_non_valid_with_sheets(self):
        sheets = {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'dummy_invalid': 'y'}}}
        with pytest.raises(colander.Invalid):
            self.make_one(self.context, self.request, sheets)

    def test_valid_with_wrong_sheet(self):
        sheets = {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'},
                                           'wrong': {'x': 'y'}}}
        self.make_one(self.context, self.request, sheets)
        assert 'wrong' not in self.request.validated['data']


class ValidatePutPropertysheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request

    def make_one(self, context, request):
        from .views import validate_put_sheet_cstructs
        validate_put_sheet_cstructs(context, request)

    def test_valid(self):
        sheets = {'sheet': DummyPropertysheet()}
        self.request.registry.content.resource_sheets.return_value = sheets
        self.request.validated = {'data': {'sheet': {'y': 'x'}}}

        self.make_one(self.context, self.request)

        assert self.request.validated['data']['sheet']['dummy_validated']
        self.request.registry.content.resource_sheets.assert_called_with(
            self.context, self.request, onlyeditable=True)


class ValidatePostPropertysheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets
        self.resource_types = request.registry.content.resource_types
        self.create = request.registry.content.create

    def make_one(self, context, request):
        from .views import validate_post_sheet_cstructs
        validate_post_sheet_cstructs(context, request)

    def test_valid(self):
        self.resource_sheets.return_value = {'sheet': DummyPropertysheet()}
        self.create.return_value = testing.DummyResource()
        self.resource_types.return_value = {'resourcex': {}}
        self.request.validated = {'content_type': 'resourcex',
                                  'data': {'sheet': {'y': 'x'}}}

        self.make_one(self.context, self.request)

        assert self.request.validated['data']['sheet']['dummy_validated']
        assert self.resource_sheets.call_args_list[0][1] == \
            {'onlycreatable': True}
        self.create.assert_called_with('resourcex', self.context,
                                       add_to_context=False,
                                       run_after_creation=False)

    def test_valid_missing_content_type(self):
        self.request.validated = {'data': {'sheet': {'y': 'x'}}}
        self.make_one(self.context, self.request)
        assert self.request.validated['data'] == {}

    def test_valid_missing_data(self):
        self.request.validated = {}
        self.make_one(self.context, self.request)
        assert self.request.validated == {}


class ValidatePUTPropertysheetNamesUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets

    def make_one(self, context, request):
        from .views import validate_put_sheet_names
        validate_put_sheet_names(context, request)

    def test_valid_no_sheets(self):
        self.resource_sheets.return_value = {}
        self.request.validated = {'data': {}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_with_sheets(self):
        self.resource_sheets.return_value = {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)

        self.resource_sheets.assert_called_with(self.context, self.request,
                                                onlyeditable=True)
        assert self.request.errors == []

    def test_valid_with_sheets_missing(self):
        self.resource_sheets.return_value = {'sheet': DummyPropertysheet(),
                                             'sheetB': DummyPropertysheet()}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_with_sheets_missing_createmandatory(self):
        sheets = {'sheet': DummyPropertysheet(),
                  'sheetB': DummyPropertysheet()}
        sheets['sheetB'].createmandatory = True
        self.resource_sheets.return_value = sheets
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_non_valid_with_sheets_wrong_name(self):
        self.resource_sheets.return_value = {'sheet': DummyPropertysheet()}
        self.request.validated = {'data': {'wrongname': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors != []


class ValidatePOSTPropertysheetNamesAddablesUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_addables = request.registry.content.resource_addables

    def make_one(self, context, request):
        from .views import validate_post_sheet_names_and_resource_type
        validate_post_sheet_names_and_resource_type(context, request)

    def test_valid_optional(self):
        self.resource_addables.return_value = {'iresourcex': {
            'sheets_mandatory': [],
            'sheets_optional': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors == []

    def test_valid_mandatory(self):
        self.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors == []

    def test_non_valid_wrong_content_type(self):
        self.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'wrong_iresource',
                                  'data': {'ipropertyx': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_wrong_sheet(self):
        self.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': [],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'wrong_iproperty': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_missing_sheet_mandatory(self):
        self.resource_addables.return_value = {'iresourcex': {
            'sheets_optional': ['propertyy'],
            'sheets_mandatory': ['ipropertyx']}}
        self.request.validated = {'content_type': 'iresourcex',
                                  'data': {'ipropertyy': {'a': 'b'}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []


class RESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder(__provides__=IResourceX)
        self.request = CorniceDummyRequest()
        resource_registry = object()
        self.request.registry.content = resource_registry

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
        self.context = DummyFolder(__provides__=IResourceX)
        registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets
        self.resource_addables = request.registry.content.resource_addables

    def make_one(self, context, request):
        from .views import ResourceRESTView
        return ResourceRESTView(context, request)

    def test_create_valid(self,):
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

    def test_get_valid_with_sheets(self):
        sheet = DummyPropertysheet()
        sheet.iface = ISheetB
        self.resource_sheets.return_value = {ISheetB.__identifier__: sheet}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        wanted = {ISheetB.__identifier__: {'dummy_cstruct': {}}}
        assert wanted == response['data']


class FubelRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder(__provides__=IResourceX)
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets

    def make_one(self, context, request):
        from .views import FubelRESTView
        return FubelRESTView(context, request)

    def test_create_valid(self,):
        from .views import validate_put_sheet_names
        from .views import validate_put_sheet_cstructs
        from .views import ResourceRESTView
        from .schemas import PUTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, ResourceRESTView)
        assert inst.validation_PUT == (PUTResourceRequestSchema,
                                       [validate_put_sheet_names,
                                        validate_put_sheet_cstructs,
                                        ])
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

    def test_put_valid_with_sheets(self):
        sheet = DummyPropertysheet()
        self.resource_sheets.return_value = {ISheetB.__identifier__: sheet}
        data = {'content_type': 'X',
                'data': {ISheetB.__identifier__: {'x': 'y'}}}
        self.request.validated = data

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {'path': '/', 'content_type': IResourceX.__identifier__}
        assert wanted == response
        assert sheet._dummy_appstruct == {'x': 'y'}


class PoolRESTViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder()
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.create = request.registry.content.create

    def make_one(self, context, request):
        from .views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create_valid(self,):
        from .views import validate_post_sheet_names_and_resource_type
        from .views import validate_post_sheet_cstructs
        from .views import FubelRESTView
        from .schemas import POSTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, FubelRESTView)
        assert inst.validation_POST ==\
            (POSTResourceRequestSchema,
             [validate_post_sheet_names_and_resource_type,
              validate_post_sheet_cstructs,
              ])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

    def test_post_valid_with_sheets(self):
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
