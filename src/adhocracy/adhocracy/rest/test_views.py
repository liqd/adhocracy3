"""Test rest.views module."""
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResource
from adhocracy.schema import Identifier
from adhocracy.schema import ReferenceSetSchemaNode
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
        from .views import SimpleRESTView
        return SimpleRESTView(context, request)

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

    def test_create(self,):
        from .views import validate_post_sheet_names_and_resource_type
        from .views import validate_post_sheet_cstructs
        from .views import SimpleRESTView
        from .schemas import POSTResourceRequestSchema
        inst = self.make_one(self.context, self.request)
        assert issubclass(inst.__class__, SimpleRESTView)
        assert inst.validation_POST ==\
            (POSTResourceRequestSchema,
             [validate_post_sheet_names_and_resource_type,
              validate_post_sheet_cstructs,
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

    def test_post_valid_item(self):
        from adhocracy.interfaces import IItem
        from adhocracy.interfaces import IItemVersion
        child = testing.DummyResource(__provides__=IItem,
                                      __parent__=self.context,
                                      __name__='child')
        first = testing.DummyResource(__provides__=IItemVersion)
        child['first'] = first
        self.create.return_value = child
        self.request.validated = {'content_type':
                                  IItemVersion.__identifier__,
                                  'data': {}}
        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {'path': '/child',
                  'content_type': IItem.__identifier__,
                  'first_version_path': '/child/first'}
        assert wanted == response


class MetaApiViewUnitTest(unittest.TestCase):

    def setUp(self):
        self.context = DummyFolder()
        resource_registry = make_mock_resource_registry()
        request = CorniceDummyRequest()
        request.registry.content = resource_registry
        self.request = request
        self.resource_types = request.registry.content.resource_types
        self.sheet_metadata = request.registry.content.sheet_metadata

        # Building blocks for dummies
        self.dummy_item_type = 'DummyItemVersion'
        self.dummy_addables = [self.dummy_item_type, 'DummyTag',
                'DummyComment']
        self.basic_dummy_sheets = ['BasicDummySheet']
        self.extended_dummy_sheets = ['EnhancedDummySheet',
                'AdvancedDummySheet']

        # Build some dummy resource descriptions
        # res1 has everything
        self.res1_meta = self._build_resource_metadata(self.dummy_item_type,
                self.dummy_addables, self.basic_dummy_sheets,
                self.extended_dummy_sheets)
        # res2 has only addables
        self.res2_meta = self._build_resource_metadata(None,
                self.dummy_addables, None, None)
        # res3 has only basic sheets
        self.res3_meta = self._build_resource_metadata(None, None,
                self.basic_dummy_sheets, None)
        # res4 has only item type and extended sheets
        self.res4_meta = self._build_resource_metadata(self.dummy_item_type,
                None, None, self.extended_dummy_sheets)

    def make_one(self, context, request):
        from .views import MetaApiView
        return MetaApiView(context, request)

    def test_get_empty_meta_api(self):
        inst = self.make_one(self.context, self.request)
        response = inst.get()
        assert sorted(response.keys()) == ['resources', 'sheets']
        assert response['resources'] == {}
        assert response['sheets'] == {}

    def _build_resource_metadata(self, item_type, addable_content_interfaces,
            basic_sheets, extended_sheets):
        """Helper method that assembles dummy resource metadata."""
        metadata = {}
        if item_type is not None:
            metadata['item_type'] = item_type
        if addable_content_interfaces:
            metadata['addable_content_interfaces'] = addable_content_interfaces
        if basic_sheets:
            metadata['basic_sheets'] = basic_sheets
        if extended_sheets:
            metadata['extended_sheets'] = extended_sheets
        return { 'metadata': metadata }

    def _check_resource_desc(self, result, metametadata):
        """Check that a resource description looks as expected."""
        assert result is not None
        # metadata as returned by the registry is wrapped in an outer
        # 'metadata' element
        metadata = metametadata['metadata']
        item_type = metadata.get('item_type')
        assert result.get('main_element_type') == item_type

        addables = metadata.get('addable_content_interfaces', [])
        extra_element_types = result.get('extra_element_types', [])
        if item_type is not None and item_type in addables:
            # main_element_type shouldn't be repeated in extra_element_types
            assert len(extra_element_types) + 1 == len(addables)
            assert item_type not in extra_element_types
        else:
            assert sorted(extra_element_types) == sorted(addables)

        basic_sheets = metadata.get('basic_sheets', [])
        extended_sheets = metadata.get('extended_sheets', [])
        sheets = result.get('sheets', [])
        assert len(sheets) == len(basic_sheets) + len(extended_sheets)
        for sheet in basic_sheets:
            assert sheet in sheets
        for sheet in extended_sheets:
            assert sheet in sheets

    def test_get_resources_via_meta_api(self):
        self.resource_types.return_value = {
                'Resource1': self.res1_meta,
                'Resource2': self.res2_meta,
                'Resource3': self.res3_meta,
                'Resource4': self.res4_meta,
                }

        inst = self.make_one(self.context, self.request)
        response = inst.get()
        resources_desc = response['resources']
        assert len(resources_desc) == 4

        # Check that descriptions are as they should be
        self._check_resource_desc(resources_desc['Resource1'], self.res1_meta)
        self._check_resource_desc(resources_desc['Resource2'], self.res2_meta)
        self._check_resource_desc(resources_desc['Resource3'], self.res3_meta)
        self._check_resource_desc(resources_desc['Resource4'], self.res4_meta)

    def _build_sheet_metadata(self, createmandatory, readonly, **fields):
        """Helper method that assembles dummy sheet metadata."""
        metadata = {
                'createmandatory': createmandatory,
                'readonly': readonly,
                }
        for fieldname, fieldtype in fields.items():
            metadata['field:' + fieldname] = fieldtype
        return metadata

    def _check_sheet_desc(self, result, metadata, expected_map):
        """Check that a sheet description looks as expected."""
        assert result is not None
        fields = result['fields']

        # metadata contains 'createmandatory' and 'readonly' as additional
        # entries
        assert len(fields) == len(metadata) - 2

        for field in fields:
            assert field['createmandatory'] == metadata['createmandatory']
            assert field['readonly'] == metadata['readonly']

            fieldname = field['name']
            assert fieldname in expected_map

            expected_values = expected_map[fieldname]
            assert field['valuetype'] == expected_values['valuetype']
            assert field['listtype'] == expected_values['listtype']

    def test_get_sheets_via_meta_api(self):
        self.resource_types.return_value = { 'Resource1': self.res1_meta }
        # Some types for testing with the expected result
        node_map = {
            'title': colander.SchemaNode(colander.String()),
            'elements': ReferenceSetSchemaNode(
                reftype='adhocracy.sheets.document.ISectionElementsReference'
            ),
            'name': Identifier(),
            'count': colander.SchemaNode(colander.Integer()),
            'follows': ReferenceSetSchemaNode(
                reftype='adhocracy.sheets.versions.IVersionableFollowsReference'
            )
        }
        expected_map = {
            'title': { 'valuetype': 'String', 'listtype': 'single' },
            'elements': {
                'valuetype': 'adhocracy.schema.AbsolutePath',
                'listtype': 'set'
            },
            'name': { 'valuetype': 'String', 'listtype': 'single' },
            'count': { 'valuetype': 'Integer', 'listtype': 'single' },
            'follows': {
                'valuetype': 'adhocracy.schema.AbsolutePath',
                'listtype': 'set'
            },
        }

        basic_meta = self._build_sheet_metadata(False, True,
                title=node_map['title'], elements=node_map['elements'])
        enhanced_meta = self._build_sheet_metadata(True, False,
                name=node_map['name'])
        advanced_meta = self._build_sheet_metadata(False, False,
                count=node_map['count'], follows=node_map['follows'])
        empty_meta = self._build_sheet_metadata(True, True)

        self.sheet_metadata.return_value = {
                'BasicDummySheet': basic_meta,
                'EnhancedDummySheet': enhanced_meta,
                'AdvancedDummySheet': advanced_meta,
                'EmptyDummySheet': empty_meta
                }

        inst = self.make_one(self.context, self.request)
        response = inst.get()
        sheets_desc = response['sheets']
        assert len(sheets_desc) == 4

        # Check that descriptions are as they should be
        self._check_sheet_desc(sheets_desc['BasicDummySheet'],
                basic_meta, expected_map)
        self._check_sheet_desc(sheets_desc['EnhancedDummySheet'],
                enhanced_meta, expected_map)
        self._check_sheet_desc(sheets_desc['AdvancedDummySheet'],
                advanced_meta, expected_map)
        self._check_sheet_desc(sheets_desc['EmptyDummySheet'],
                empty_meta, expected_map)
