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
import json
import pytest
import unittest


############
#  helper  #
############

class IResourceX(IResource):
    pass


class IPropertyB(IProperty):
    taggedValue("schema", "adhocracy.rest.test_views.CountSchema")


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
        return "0000001"

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


@patch('adhocracy.resources.registry.ResourceContentRegistry', autospec=True)
def make_mock_resource_registry(mock_registry=None):
    return mock_registry.return_value


@patch('adhocracy.resources.registry.ResourceContentRegistry', autospec=True)
def make_mock_resource_registry_with_mock_type(iresource, mock_registry=None):
    registry = mock_registry.return_value
    registry.typeof.return_value = iresource.__identifier__
    return registry


@patch('adhocracy.properties.ResourcePropertySheetAdapter')
def make_mock_propertysheet(iproperty, dummy_propertysheet=None):
    propertysheet = dummy_propertysheet.return_value
    propertysheet.iface = iproperty
    schema = resolve(iproperty.getTaggedValue("schema"))
    propertysheet.schema = schema()
    cstruct = propertysheet.schema.serialize()
    propertysheet.get_cstruct.return_value = cstruct
    propertysheet.permission_view = "view"
    propertysheet.permission_edit = "edit"
    return propertysheet


##########
#  tests #
##########

class ValidateRequestWithCorniceSchema(unittest.TestCase):

    def make_one(self, schema, request):
        from .views import validate_request_with_cornice_schema
        validate_request_with_cornice_schema(schema, request)

    def setUp(self):
        self.config = testing.setUp()
        self.request = CorniceDummyRequest()
        setattr(self.request, 'errors', Errors(self.request))

    def test_valid_request_body(self):
        schema = CountSchema
        self.request.body = '{"count": "1"}'
        self.make_one(schema, self.request)
        wanted = {"count": 1}
        assert self.request.validated == wanted

    def test_valid_request_body_none(self):
        schema = CountSchema
        self.request.body = ''
        self.make_one(schema, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_valid_request_body_empty_dict(self):
        schema = CountSchema
        self.request.body = '{}'
        self.make_one(schema, self.request)
        wanted = {}
        assert self.request.validated == wanted

    def test_non_valid_request_body(self):
        schema = CountSchema
        self.request.body = '{"count": "wrong_value"}'
        self.make_one(schema, self.request)
        assert self.request.errors != []

    def test_non_valid_remove_validated_dict(self):
        schema = CountSchema
        self.request.validated == {"secret_data": "buh"}
        self.request.body = '{"count": "wrong_value"}'
        self.make_one(schema, self.request)
        assert self.request.validated == {}


class ValidatePUTPropertysheetNamesUnitTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.context = testing.DummyResource()
        request = CorniceDummyRequest(registry=self.config.registry)
        resource_registry = make_mock_resource_registry()
        request.registry.content = resource_registry
        self.request = request

    def make_one(self, context, request):
        from .views import validate_put_propertysheet_names
        validate_put_propertysheet_names(context, request)

    def test_valid_no_propertysheets(self):
        propertysheets = self.request.registry.content.resource_propertysheets
        propertysheets.return_value = {}
        self.request.validated = {"data": {}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_valid_with_propertysheets(self):
        self.request.registry.content.resource_propertysheets.return_value =\
            {'propertysheet': Dummy()}
        self.request.validated = {"data": {"propertysheet": {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors == []

    def test_non_valid_with_propertysheets_wrong_name(self):
        self.request.registry.content.resource_propertysheets.return_value =\
            {'propertysheet': Dummy()}
        self.request.validated = {"data": {"wrongname": {'x': 'y'}}}
        self.make_one(self.context, self.request)
        assert self.request.errors != []

    def test_non_valid_with_propertysheets_no_permission(self):
        self.request.registry.content.resource_propertysheets.return_value =\
            {'propertysheet': Dummy()}
        self.request.validated = {"data": {"wrongname": {'x': 'y'}}}
        self.config.testing_securitypolicy(userid='reader', permissive=False)
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
        from .views import validate_post_propertysheet_names_addables
        validate_post_propertysheet_names_addables(context, request)

    def test_valid(self):
        registry = self.request.registry.content
        registry.resource_addable_types.return_value = {"iresourcex":
                                                        set(["ipropertyx"])}
        self.request.validated = {"content_type": "iresourcex",
                                  "data": {"ipropertyx": {"a": "b"}}}

        self.make_one(self.context, self.request)

        assert self.request.errors == []

    def test_non_valid_wrong_iresource(self):
        registry = self.request.registry.content
        registry.resource_addable_types.return_value = {"iresourcex":
                                                        set(["ipropertyx"])}
        self.request.validated = {"content_type": "wrong_iresource",
                                  "data": {"ipropertyx": {"a": "b"}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_wrong_iproperty(self):
        registry = self.request.registry.content
        registry.resource_addable_types.return_value = {"iresourcex":
                                                        set(["ipropertyx"])}
        self.request.validated = {"content_type": "iresourcex",
                                  "data": {"wrong_iproperty": {"a": "b"}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    def test_non_valid_missing_iproperty(self):
        registry = self.request.registry.content
        registry.resource_addable_types.return_value = {"iresourcex":
                                                        set(["ipropertyx",
                                                             "ipropertyy"])}
        self.request.validated = {"content_type": "iresourcex",
                                  "data": {"ipropertyx": {"a": "b"}}}

        self.make_one(self.context, self.request)

        assert self.request.errors != []

    #FIXME:  how to find out what iproperties are needed for posting?
    #        maybe mark iproperty "readonly" or "addable"?


# FIXME: split View in subclasses?
class ResourceViewUnitTest(unittest.TestCase):

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
        from .views import ResourceView
        return ResourceView(context, request)

    def test_create_valid(self,):
        inst = self.make_one(self.context, self.request)
        assert inst.context is self.context
        assert inst.registry == self.request.registry.content
        assert inst.request is self.request
        assert inst.request.errors == []
        assert inst.request.validated == {}
        assert hasattr(inst, "sheets_all")
        assert hasattr(inst, "sheets_view")
        assert hasattr(inst, "sheets_edit")
        assert hasattr(inst, "addables")

    def test_option_valid_no_propertysheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.request.registry.content.resource_propertysheets.return_value = {}
        self.request.registry.content.resource_addable_types.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.option()

        wanted = OPTIONResourceResponseSchema().serialize()
        assert wanted == response

    def test_option_valid_with_propertysheets_and_addables(self):
        from adhocracy.rest.schemas import OPTIONResourceResponseSchema
        self.request.registry.content.resource_propertysheets.return_value = {
            "propertyx": Dummy()}
        self.request.registry.content.resource_addable_types.return_value = {
            "resourcex": set(["propertyx"])}
        inst = self.make_one(self.context, self.request)
        response = inst.option()

        wanted = OPTIONResourceResponseSchema().serialize()
        wanted["PUT"]["request_body"] = {"data": {"propertyx": {}}}
        wanted["GET"]["response_body"]["data"]["propertyx"] = {}
        wanted["POST"]["request_body"] = [{"content_type": "resourcex",
                                           "data": {"propertyx": {}}}]
        assert wanted == response

    def test_get_valid_no_propertysheets(self):
        from adhocracy.rest.schemas import GETResourceResponseSchema
        self.request.registry.content.resource_propertysheets.return_value = {}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        wanted = GETResourceResponseSchema().serialize()
        wanted["path"] = "/"
        wanted["data"] = {}
        wanted["content_type"] = IResourceX.__identifier__
        assert wanted == response

    def test_get_valid_with_propertysheets(self):
        propertysheet = make_mock_propertysheet(IPropertyB)
        self.request.registry.content.resource_propertysheets.return_value = {
            IPropertyB.__identifier__: propertysheet}

        inst = self.make_one(self.context, self.request)
        response = inst.get()

        data = propertysheet.schema.serialize()
        wanted = {IPropertyB.__identifier__: data}
        assert wanted == response["data"]

    def test_put_valid_no_propertysheets(self):
        self.request.registry.content.resource_propertysheets.return_value = {}
        self.request.body = '{"content_type": "X", "data": {}}'

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {"path": "/", "content_type": IResourceX.__identifier__}
        assert wanted == response

    def test_put_valid_with_propertysheets(self):
        propertysheet = make_mock_propertysheet(IPropertyB)
        propertysheet.set_cstruct.return_value = True
        self.request.registry.content.resource_propertysheets.return_value = {
            IPropertyB.__identifier__: propertysheet}
        body = json.dumps({"content_type": IResource.__identifier__,
                           "data": {IPropertyB.__identifier__: {"x": "y"}}})
        self.request.body = body

        inst = self.make_one(self.context, self.request)
        response = inst.put()

        wanted = {"path": "/", "content_type": IResourceX.__identifier__}
        assert wanted == response
        assert propertysheet.set_cstruct.called

    def test_put_non_valid_with_propertysheets_raise_invalid(self):
        propertysheet = make_mock_propertysheet(IPropertyB)
        self.request.registry.content.resource_propertysheets.return_value = {
            IPropertyB.__identifier__: propertysheet}
        body = json.dumps({"content_type": IResource.__identifier__,
                           "data": {IPropertyB.__identifier__: {"x": "y"}}})
        self.request.body = body
        invalid_node = colander.SchemaNode(typ=colander.String())
        propertysheet.set_cstruct.side_effect = colander.Invalid(invalid_node)

        inst = self.make_one(self.context, self.request)
        with pytest.raises(colander.Invalid):
            inst.put()

    def test_post_valid_with_propertysheets(self):
        from adhocracy.properties.interfaces import IName
        propertysheet = make_mock_propertysheet(IPropertyB)
        propertysheet.set_cstruct.return_value = True
        registry = self.request.registry.content
        registry.create.return_value = testing.DummyResource()
        registry.resource_propertysheets.return_value =\
            {IName.__identifier__: propertysheet}
        registry.resource_addable_types.return_value =\
            {"iresourcex": set([IName.__identifier__])}
        body = {"content_type": "iresourcex",
                "data": {IName.__identifier__: {"name": "child"}}}
        self.request.body = json.dumps(body)

        inst = self.make_one(self.context, self.request)
        response = inst.post()

        wanted = {"path": "/child", "content_type": IResourceX.__identifier__}
        assert wanted == response
        assert "child" in self.context

    def test_post_non_valid_with_propertysheets_raise_invalid(self):
        propertysheet = make_mock_propertysheet(IPropertyB)
        propertysheet.set_cstruct.return_value = True
        invalid_node = colander.SchemaNode(typ=colander.String())
        propertysheet.set_cstruct.side_effect = colander.Invalid(invalid_node)
        registry = self.request.registry.content
        registry.create.return_value = testing.DummyResource()
        registry.resource_propertysheets.return_value = {"ipropertyx":
                                                         propertysheet}
        registry.resource_addable_types.return_value = {"iresourcex":
                                                        set(["ipropertyx"])}
        self.request.body = '{"content_type": "iresourcex", "data":'\
                            '{"ipropertyx": {"a": "b"}}}'

        inst = self.make_one(self.context, self.request)
        with pytest.raises(colander.Invalid):
            inst.post()
