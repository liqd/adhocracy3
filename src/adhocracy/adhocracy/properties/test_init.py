from adhocracy.properties.interfaces import IProperty
from collections import UserDict
from pyramid.testing import DummyRequest
from substanced.interfaces import IFolder
from unittest.mock import patch
from pyramid import testing
from zope.interface import (
    Interface,
    implementer,
    taggedValue,
)
import colander
import pytest
import unittest


############
#  helper  #
############


@implementer(IFolder)
class DummyFolder(UserDict):
    interfaces = []
    __parent__ = None


class InterfaceY(Interface):
    pass


class IPropertyA(IProperty):
    taggedValue("schema", "adhocracy.properties.test_init.CountSchema")


class IPropertyB(IProperty):
    taggedValue("schema", "adhocracy.properties.test_init.CountSchema")


class CountSchema(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


class IPropertyZ(IProperty):
    taggedValue("schema",
                "adhocracy.properties.test_init.CountSchemaMissingDefault")


class CountSchemaMissingDefault(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                missing=colander.drop)


class IPropertyY(IProperty):
    taggedValue("schema",
                "adhocracy.properties.test_init.CountSchemaMissingMissing")


class CountSchemaMissingMissing(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0)


class IExtendPropertyB(IPropertyB):
    taggedValue("schema",
                "adhocracy.properties.test_init.ExtendCountSchema")
    taggedValue("key", IPropertyB.__identifier__)


class ExtendCountSchema(CountSchema):
    newattribute = colander.SchemaNode(colander.String(),
                                       default="",
                                       missing=colander.drop)


@patch('substanced.objectmap.ObjectMap', autospec=True)
def make_folder_with_objectmap(dummyobjectmap=None):
    folder = DummyFolder()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


##########
#  tests #
##########

class ResourcePropertySheetAdapterUnitTests(unittest.TestCase):

    def make_one(self, *args):
        from . import ResourcePropertySheetAdapter
        return ResourcePropertySheetAdapter(*args)

    def test_initcreate_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        context = DummyFolder()
        request = None
        iproperty = IPropertyB
        inst = self.make_one(context, request, iproperty)
        assert inst.context == context
        assert inst.request == request
        assert inst.permission_view == "view"
        assert inst.permission_edit == "edit"
        assert isinstance(inst.schema, CountSchema)
        assert inst.key == IPropertyB.__identifier__
        assert verifyObject(IResourcePropertySheet, inst) is True

    def test_initcreate_non_valid_non_mapping_context(self):
        with pytest.raises(AssertionError):
            self.make_one(object(), None, IPropertyB)

    def test_initcreate_non_valid_non_iproperty_iface(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyFolder(), None, InterfaceY)

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def test_initcreate_references(self, dummy_reference_node=None):
        node = dummy_reference_node.return_value
        node.name = "references"
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.schema.children.append(node)
        assert inst._references == {"references": IPropertyB.__identifier__
                                    + ":references"}

    def test_initget_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.get() == {"count": 0}

    def test_initget_non_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst._data["count"] = 11
        assert inst.get() == {"count": 11}

    def test_initset_valid(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.set({"count": 11}) is True
        assert inst.get() == {"count": 11}

    def test_initset_valid_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.set({}) is False
        assert inst.get() == {"count": 0}

    def test_initset_valid_omit_str(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.set({"count": 11}, omit="count") is False

    def test_initset_valid_omit_tuple(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.set({"count": 11}, omit=("count",)) is False

    def test_initset_valid_omit_wrong_key(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.set({"count": 11}, omit=("wrongkey",)) is True

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def test_initset_valid_references(self, dummy_reference_node=None):
        node = dummy_reference_node.return_value
        node.name = "references"
        node.deserialize.return_value = []
        context = make_folder_with_objectmap()
        inst = self.make_one(context, None, IPropertyB)
        inst.schema.children.append(node)
        inst.set({"references": [1]})
        om = context.__objectmap__
        reftype = inst._references["references"]
        assert om.connect.assert_called_once_with(context, 1, reftype) is None

    def test_initget_cstruct_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        assert inst.get_cstruct() == {"count": "0"}

    def test_initget_cstruct_non_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst._data["count"] = 11
        assert inst.get_cstruct() == {"count": "11"}

    def test_initset_cstruct_valid(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.set_cstruct({"count": "11"})
        assert inst.get_cstruct() == {"count": "11"}

    def test_initset_cstruct_valid_empty(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.set_cstruct({})
        assert inst.get_cstruct() == {"count": "0"}

    def test_initset_cstruct_valid_with_name_conflicts(self):
        context = DummyFolder()
        inst1 = self.make_one(context, None, IPropertyB)
        inst1.set_cstruct({"count": "1"})
        inst2 = self.make_one(context, None, IPropertyA)
        inst2.set_cstruct({"count": "2"})
        assert inst1.get_cstruct() == {"count": "1"}
        assert inst2.get_cstruct() == {"count": "2"}

    def test_initset_cstruct_valid_readonly(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.schema.children[0].readonly = True
        inst.set_cstruct({"count": "1"})
        assert inst.get_cstruct() == {"count": "0"}

    def test_initget_cstruct_non_valid_missing_default_value(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyFolder(), None, IPropertyZ)

    def test_initget_cstruct_non_valid_missing_missing_value(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyFolder(), None, IPropertyY)

    def test_initset_cstruct_non_valid_wrong_type(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        with pytest.raises(colander.Invalid):
            inst.set_cstruct({"count": "wrongnumber"})

    def test_initset_cstruct_non_valid_required(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.schema.children[0].required_ = True
        # FIXME: the attriute required is automatically set
        # without "missing" value
        with pytest.raises(colander.Invalid):
            inst.set_cstruct({})

    def test_initset_cstruct_non_valid_required_and_readonly(self):
        inst = self.make_one(DummyFolder(), None, IPropertyB)
        inst.schema.children[0].required_ = True
        inst.schema.children[0].readonly = True
        with pytest.raises(AssertionError):
            inst.set_cstruct({})


class PoolPropertySheetUnitTest(unittest.TestCase):

    def make_one(self, *args):
        from . import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(*args)

    def test_initcreate_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        from adhocracy.properties.interfaces import IPool
        from pyramid.httpexceptions import HTTPNotImplemented
        inst = self.make_one(DummyFolder(), None, IPool)
        assert verifyObject(IResourcePropertySheet, inst) is True
        with pytest.raises(HTTPNotImplemented):
            inst.set_cstruct({})
        with pytest.raises(HTTPNotImplemented):
            inst.set({})

    def test_initcreate_non_valid(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyFolder(), None, IPropertyB)

    def test_initget_empty(self):
        from adhocracy.properties.interfaces import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = []
        inst = self.make_one(context, None, IPool)
        assert inst.get() == {"elements": []}

    def test_initget_not_empty(self):
        from adhocracy.properties.interfaces import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = [1]
        context.__objectmap__.path_for.return_value = ("", "child1")
        context["child1"] = DummyFolder()
        inst = self.make_one(context, None, IPool)
        assert inst.get() == {"elements": ["/child1"]}


class ResourcePropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def make_one(self, config, context, request, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        request = DummyRequest()
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, request, iface),
                                               IResourcePropertySheet)
        return inst

    def register_propertysheet_adapter(self, config, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.properties.interfaces import IIProperty
        from adhocracy.properties import ResourcePropertySheetAdapter
        from pyramid.interfaces import IRequest
        from zope.interface import alsoProvides
        alsoProvides(iface, IIProperty)
        self.config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                             (iface, IRequest, IIProperty),
                                             IResourcePropertySheet)

    def test_initregister_ipropertysheet_adapter_inheritance(self):
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = DummyFolder()
        inst_extend = self.make_one(self.config, context,
                                    DummyRequest(), IExtendPropertyB)
        assert IPropertyB.providedBy(context)
        assert IExtendPropertyB.providedBy(context)
        assert "count" in inst_extend.get()
        assert "newattribute" in inst_extend.get()

    def test_initincludeme_register_ipropertysheet_adapter_extend(self):
        self.register_propertysheet_adapter(self.config, IPropertyB)
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = DummyFolder()
        inst_extend = self.make_one(self.config, context,
                                    DummyRequest(), IExtendPropertyB)
        inst = self.make_one(self.config, context,
                             DummyRequest(), IPropertyB)
        inst_extend.set({"count": 1})
        assert inst_extend.key == inst.key
        assert inst.get() == {"count": 1}
        assert inst_extend.get() == {"count": 1, "newattribute": ""}
        inst.set({"count": 2})
        assert inst_extend.get() == {"count": 2, "newattribute": ""}
        assert inst.get() == {"count": 2}

    def test_initincludeme_register_ipropertysheet_adapter_iname(self):
        from adhocracy.properties.interfaces import IName
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(), IName)
        assert inst.iface is IName

    def test_initincludeme_register_ipropertysheet_adapter_inamereadonly(self):
        from adhocracy.properties.interfaces import INameReadOnly
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(),
                             INameReadOnly)
        assert inst.iface is INameReadOnly

    def test_initincludeme_register_ipropertysheet_adapter_iversions(self):
        from adhocracy.properties.interfaces import IVersions
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(),
                             IVersions)
        assert inst.iface is IVersions

    def test_initincludeme_register_ipropertysheet_adapter_itags(self):
        from adhocracy.properties.interfaces import ITags
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(), ITags)
        assert inst.iface is ITags

    def test_initincludeme_register_ipropertysheet_adapter_iversionable(self):
        from adhocracy.properties.interfaces import IVersionable
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(),
                             IVersionable)
        assert inst.iface is IVersionable

    def test_initincludeme_register_ipropertysheet_adapter_ipool(self):
        from adhocracy.properties.interfaces import IPool
        from adhocracy.properties import PoolPropertySheetAdapter
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyFolder(), DummyRequest(), IPool)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IPool
