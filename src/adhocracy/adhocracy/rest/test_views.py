"""Test rest.views module."""
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

    def __init__(self, registry=None):
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


@patch('adhocracy.registry.ResourceContentRegistry', autospec=True)
def make_mock_resource_registry(mock_registry=None):
    return mock_registry.return_value


def make_resources_metadata(metadata):
    """Helper method that assembles dummy resource metadata.

    It returns the same structure as the resources_metadata method from
    adhocracy.registry.

    """
    iresource = metadata.iresource
    return {iresource.__identifier__: {'name': iresource.__identifier__,
                                       'iface': iresource,
                                       'metadata': metadata}
            }


##########
#  tests #
##########


class ValidateRequestDataUnitTest(unittest.TestCase):

    def _make_one(self, *args, **kw):
        from adhocracy.rest.views import validate_request_data
        validate_request_data(*args, **kw)

    def setUp(self):
        self.request = CorniceDummyRequest()
        self.context = testing.DummyResource()
        setattr(self.request, 'errors', Errors(self.request))

    def test_valid_with_schema_and_request_has_json_data_but_missing_deserializer(self):
        data = {'data': True}
        self.request.json =  data
        self._make_one(self.context, self.request, colander.MappingSchema)
        assert hasattr(self.request, 'deserializer')
        data_deserialized = self.request.deserializer(self.request)
        assert data_deserialized

    def test_valid_wrong_method_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self.request.method = 'wrong_method'
        self._make_one(self.context, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_no_schema_with_data(self):
        self.request.body = '{"wilddata": "1"}'
        self._make_one(self.context, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_no_data(self):
        schema = CountSchema
        self.request.body = ''
        self._make_one(self.context, self.request, schema=schema)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_no_data_empty_dict(self):
        schema = CountSchema
        self.request.body = '{}'
        self._make_one(schema, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_with_schema_with_data(self):
        schema = CountSchema
        self.request.body = '{"count": "1"}'
        self._make_one(self.context, self.request, schema=schema)
        wanted = {'count': 1}
        assert self.request.validated == wanted

    def test_non_valid_with_schema_wrong_data(self):
        from cornice.util import _JSONError
        schema = CountSchema
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(schema, self.request, schema=schema)
        assert self.request.errors != []

    def test_non_valid_with_schema_wrong_data_cleanup(self):
        from cornice.util import _JSONError
        schema = CountSchema
        self.request.validated == {'secret_data': 'buh'}
        self.request.body = '{"count": "wrong_value"}'
        with pytest.raises(_JSONError):
            self._make_one(schema, self.request, schema=schema)
        assert self.request.validated == {}

    def test_valid_with_extra_validator(self):
        schema = CountSchema

        def validator1(context, request):
            request.validated = "validator1"

        self._make_one(schema, self.request, extra_validators=[validator1])
        assert self.request.validated == "validator1"


class ValidateSheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        self.request = CorniceDummyRequest()

    def _make_one(self, *args):
        from adhocracy.rest.views import validate_sheet_cstructs
        validate_sheet_cstructs(*args)

    def test_valid_no_sheets(self):
        sheets = {}
        self.request.validated = {'data': {}}
        self._make_one(self.context, self.request, sheets)
        assert self.request.validated == {'data': {}}

    def test_valid_no_sheets_no_data(self):
        sheets = {}
        self.request.validated = {}
        self._make_one(self.context, self.request, sheets)
        assert self.request.validated == {}

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid_with_sheets(self, dummy_sheet=None):
        sheet = dummy_sheet.return_value
        sheet.validate_cstruct.return_value = 'validated'
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self._make_one(self.context, self.request, {'sheet': sheet})
        assert self.request.validated['data']['sheet'] == 'validated'

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_non_valid_with_sheets(self, dummy_sheet=None):
        sheet = dummy_sheet.return_value
        sheet.validate_cstruct.side_effect = colander.Invalid(None)
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        with pytest.raises(colander.Invalid):
            self._make_one(self.context, self.request, {'sheet': sheet})

    def test_valid_with_wrong_sheet(self):
        self.request.validated = {'data': {'wrong': {'x': 'y'}}}
        self._make_one(self.context, self.request, {})
        assert 'wrong' not in self.request.validated['data']


class ValidatePutSheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = resource_registry.resource_sheets

    def make_one(self, context, request):
        from adhocracy.rest.views import validate_put_sheet_cstructs
        validate_put_sheet_cstructs(context, request)

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid(self, dummy_sheet=None):
        sheet = dummy_sheet.return_value
        sheets = {'sheet': sheet}
        self.resource_sheets.return_value = sheets
        self.request.validated = {'data': {'sheet': {'y': 'x'}}}

        self.make_one(self.context, self.request)

        assert self.request.validated['data']['sheet']['dummy_validated']
        self.request.registry.content.resource_sheets.assert_called_with(
            self.context, self.request, onlyeditable=True)


class ValidatePostSheetCstructsUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets
        self.resource_types = request.registry.content.resources_metadata
        self.create = request.registry.content.create

    def make_one(self, context, request):
        from adhocracy.rest.views import validate_post_sheet_cstructs
        validate_post_sheet_cstructs(context, request)

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid(self, dummy_sheet=None):
        self.resource_sheets.return_value = {'sheet': dummy_sheet.return_value}
        self.create.return_value = testing.DummyResource()
        self.resource_types.return_value = {'resourcex': {}}
        self.request.validated = {'content_type': 'resourcex',
                                  'data': {'sheet': {'y': 'x'}}}

        self.make_one(self.context, self.request)

        assert self.request.validated['data']['sheet']['dummy_validated']
        assert self.resource_sheets.call_args_list[0][1] == {'onlycreatable': True}
        self.create.assert_called_with('resourcex', run_after_creation=False)

    def test_valid_missing_content_type(self):
        self.request.validated = {'data': {'sheet': {'y': 'x'}}}
        self.make_one(self.context, self.request)
        assert self.request.validated['data'] == {}

    def test_valid_missing_data(self):
        self.request.validated = {}
        self.make_one(self.context, self.request)
        assert self.request.validated == {}


class ValidatePUTSheetNamesUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_sheets = request.registry.content.resource_sheets

    def make_one(self, context, request):
        from adhocracy.rest.views import validate_put_sheet_names
        validate_put_sheet_names(context, request)

    def test_valid_no_sheets(self):
        self.resource_sheets.return_value = {}
        self.request.validated = {'data': {}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid_with_sheets(self, dummy_sheet=None):
        self.resource_sheets.return_value = {'sheet': dummy_sheet.return_value}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)

        self.resource_sheets.assert_called_with(self.context, self.request,
                                                onlyeditable=True)
        assert self.request.errors == []

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid_with_sheets_missing(self, dummy_sheet=None):
        self.resource_sheets.return_value = {'sheet': dummy_sheet.return_value,
                                             'sheetB': dummy_sheet.return_value}
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_valid_with_sheets_missing_createmandatory(self, dummy_sheet=None):
        sheets = {'sheet': dummy_sheet.return_value,
                  'sheetB': dummy_sheet.return_value}
        sheets['sheetB'].createmandatory = True
        self.resource_sheets.return_value = sheets
        self.request.validated = {'data': {'sheet': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    @patch('adhocracy.sheets.GenericResourceSheet')
    def test_non_valid_with_sheets_wrong_name(self, dummy_sheet=None):
        self.resource_sheets.return_value = {'sheet': dummy_sheet.return_value}
        self.request.validated = {'data': {'wrongname': {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors != []


class ValidatePOSTSheetNamesAddablesUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = testing.DummyResource()
        request = CorniceDummyRequest()
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request
        self.resource_addables = request.registry.content.resource_addables

    def make_one(self, context, request):
        from adhocracy.rest.views import \
            validate_post_sheet_names_and_resource_type
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

    def test_get_item_valid_no_sheets(self):
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        context = testing.DummyResource(__provides__=IItem)
        context['firt'] = testing.DummyResource(__provides__=IItemVersion)

        inst = self.make_one(context, self.request)

        wanted = {'path': '/', 'data': {},
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/firt'}
        assert inst.get() == wanted


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
        from .views import PoolRESTView
        return PoolRESTView(context, request)

    def test_create(self, ):
        from .views import validate_post_sheet_names_and_resource_type
        from .views import validate_post_sheet_cstructs
        from .views import SimpleRESTView
        from .schemas import POSTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == \
               (POSTResourceRequestSchema,
                [validate_post_sheet_names_and_resource_type,
                 validate_post_sheet_cstructs
                 ])
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
        from .views import ItemRESTView
        return ItemRESTView(context, request)

    def test_create(self, ):
        from .views import validate_post_sheet_names_and_resource_type
        from .views import validate_post_sheet_cstructs
        from .views import validate_post_root_versions
        from .views import SimpleRESTView
        from .schemas import POSTItemRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST == \
               (POSTItemRequestSchema,
                [validate_post_sheet_names_and_resource_type,
                 validate_post_root_versions,
                 validate_post_sheet_cstructs,
                 ])
        assert 'options' in dir(inst)
        assert 'get' in dir(inst)
        assert 'put' in dir(inst)

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
        metas = make_resources_metadata(self.resource_meta)
        self.resources_metadata.return_value = metas
        inst = self.make_one()
        resp = inst.get()
        assert IResource.__identifier__ in resp['resources']
        assert resp['resources'][IResource.__identifier__] == {'sheets': []}

    def test_get_resources_with_sheets_metadata(self):
        metas = make_resources_metadata(self.resource_meta._replace(
            basic_sheets=[ISheet],
            extended_sheets=[ISheetB]))
        self.resources_metadata.return_value = metas
        inst = self.make_one()

        resp = inst.get()['resources']

        wanted_sheets = [ISheet.__identifier__, ISheetB.__identifier__]
        assert wanted_sheets == resp[IResource.__identifier__]['sheets']

    def test_get_resources_with_element_types_metadata(self):
        metas = make_resources_metadata(self.resource_meta._replace(
            element_types=[IResource, IResourceX]))
        self.resources_metadata.return_value = metas
        inst = self.make_one()

        resp = inst.get()['resources']

        wanted = [IResource.__identifier__, IResourceX.__identifier__]
        assert wanted == resp[IResource.__identifier__]['element_types']

    def test_get_resources_with_item_type_metadata(self):
        metas = make_resources_metadata(self.resource_meta._replace(
            item_type=IResourceX))
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
        assert field_metadata['createmandatory'] is False
        assert field_metadata['readonly'] is False
        assert field_metadata['name'] == 'test'
        assert 'valuetype' in field_metadata

    def test_get_followed_by_field_of_versionable_sheet(self):
        from adhocracy.sheets.versions import IVersionable

        class SchemaF(self.sheet_meta.schema_class):
            followed_by = colander.SchemaNode(colander.List())
        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        sheet_name = IVersionable.__identifier__
        self.sheets_metadata.return_value = {sheet_name: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][sheet_name]

        field_metadata = response['fields'][0]
        assert field_metadata['readonly'] is True

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
        from adhocracy.schema import Identifier

        class SchemaF(self.sheet_meta.schema_class):
            test = colander.SchemaNode(Identifier())

        sheet_meta = self.sheet_meta._replace(schema_class=SchemaF)
        self.sheets_metadata.return_value = {ISheet.__identifier__: sheet_meta}
        inst = self.make_one()

        response = inst.get()['sheets'][ISheet.__identifier__]

        field_metadata = response['fields'][0]
        assert 'containertype' not in field_metadata
        assert field_metadata['valuetype'] == 'adhocracy.schema.Identifier'

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

    def test_decorates_rest_method(self):
        from adhocracy.rest.views import validate_request_data_decorator
        request = testing.DummyRequest(method='GET',
                                       errors=[])
        request.registry.content = testing.DummyResource()
        context = testing.DummyResource()
        def dummy_validate(context, request):
            request.validated = {'data': True}
        class DummyOriginalView:
            validation_GET = (None, [dummy_validate])
        @validate_request_data_decorator()
        class DummyView(testing.DummyResource):
            __original_view__ = DummyOriginalView

        DummyView(context, request)

        assert request.validated == {'data': True}






