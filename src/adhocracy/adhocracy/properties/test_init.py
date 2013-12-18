from adhocracy.properties.interfaces import IProperty
from pyramid.testing import (
    DummyRequest,
    DummyResource,
)
from unittest.mock import call
from unittest.mock import patch
from pyramid import testing
from zope.interface import (
    Interface,
    taggedValue,
)
import colander
import pytest
import unittest


############
#  helper  #
############


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
    folder = testing.DummyResource()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


##########
#  tests #
##########

class ResourcePropertySheetAdapterUnitTests(unittest.TestCase):

    def make_one(self, *args):
        from . import ResourcePropertySheetAdapter
        return ResourcePropertySheetAdapter(*args)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        context = DummyResource()
        request = None
        iproperty = IPropertyB
        inst = self.make_one(context, request, iproperty)
        assert inst.context == context
        assert inst.request == request
        assert inst.permission_view == "view"
        assert inst.permission_edit == "edit"
        assert inst.readonly == False
        assert isinstance(inst.schema, CountSchema)
        assert inst.key == IPropertyB.__identifier__
        assert verifyObject(IResourcePropertySheet, inst) is True

    def test_create_non_valid_non_mapping_context(self):
        with pytest.raises(AssertionError):
            self.make_one(object(), None, IPropertyB)

    def test_create_non_valid_non_iproperty_iface(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyResource(), None, InterfaceY)

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def test_create_references(self, dummy_reference_node=None):
        node = dummy_reference_node.return_value
        node.name = "references"
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst.schema.children.append(node)
        assert inst._references == {"references": IPropertyB.__identifier__
                                    + ":references"}

    def test_get_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.get() == {"count": 0}

    def test_get_non_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst._data["count"] = 11
        assert inst.get() == {"count": 11}

    def test_set_valid(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.set({"count": 11}) is True
        assert inst.get() == {"count": 11}

    def test_set_valid_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.set({}) is False
        assert inst.get() == {"count": 0}

    def test_set_valid_omit_str(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.set({"count": 11}, omit="count") is False

    def test_set_valid_omit_tuple(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.set({"count": 11}, omit=("count",)) is False

    def test_set_valid_omit_wrong_key(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.set({"count": 11}, omit=("wrongkey",)) is True

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def _set_valid_references(self, old_oids, new_oids,
                              expected_connect_oids,
                              expected_disconnect_oids,
                              dummy_reference_node=None):

        node = dummy_reference_node.return_value
        node.name = "references"
        node.deserialize.return_value = old_oids
        #default value
        node.serialize.return_value = []
        context = make_folder_with_objectmap()
        om = context.__objectmap__
        inst = self.make_one(context, None, IProperty)

        inst.schema.children.append(node)

        inst.set({"references": new_oids})
        reftype = inst._references["references"]
        assert om.connect.call_count == len(expected_connect_oids)
        for oid in expected_connect_oids:
            assert om.connect.assert_has_calls(
                call(context, oid, reftype)) is None
        assert om.disconnect.call_count == len(expected_disconnect_oids)
        for oid in expected_disconnect_oids:
            assert om.disconnect.assert_has_calls(
                call(context, oid, reftype)) is None

    def test_set_valid_references_added(self):
        self._set_valid_references({1, 3}, {1, 2, 3, 4}, {2, 4}, {})

    def test_set_valid_references_removed(self):
        self._set_valid_references({5, 6, 7, 8}, {5, 7}, {}, {6, 8})

    def test_set_valid_references_added_and_removed(self):
        self._set_valid_references({1, 2, 3, 4}, {3, 4, 5, 6}, {5, 6}, {1, 2})

    def test_set_valid_references_unchanged(self):
        self._set_valid_references({3, 4, 5}, {3, 4, 5}, {}, {})

    def test_get_cstruct_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        assert inst.get_cstruct() == {"count": "0"}

    def test_get_cstruct_non_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst._data["count"] = 11
        assert inst.get_cstruct() == {"count": "11"}

    def test_set_cstruct_valid(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst.set_cstruct({"count": "11"})
        assert inst.get_cstruct() == {"count": "11"}

    def test_set_cstruct_valid_empty(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst.set_cstruct({})
        assert inst.get_cstruct() == {"count": "0"}

    def test_set_cstruct_valid_with_name_conflicts(self):
        context = DummyResource()
        inst1 = self.make_one(context, None, IPropertyB)
        inst1.set_cstruct({"count": "1"})
        inst2 = self.make_one(context, None, IPropertyA)
        inst2.set_cstruct({"count": "2"})
        assert inst1.get_cstruct() == {"count": "1"}
        assert inst2.get_cstruct() == {"count": "2"}

    def test_set_cstruct_valid_readonly(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        inst.schema.children[0].readonly = True
        inst.set_cstruct({"count": "1"})
        assert inst.get_cstruct() == {"count": "0"}

    def test_get_cstruct_non_valid_missing_default_value(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyResource(), None, IPropertyZ)

    def test_get_cstruct_non_valid_missing_missing_value(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyResource(), None, IPropertyY)

    def test_set_cstruct_non_valid_wrong_type(self):
        inst = self.make_one(DummyResource(), None, IPropertyB)
        with pytest.raises(colander.Invalid):
            inst.set_cstruct({"count": "wrongnumber"})

    # TODO
    # def test_set_cstruct_non_valid_required(self):
    #     inst = self.make_one(DummyResource(), None, IPropertyB)
    #     inst.schema.children[0].required_ = True
    #     # FIXME: the attriute required is automatically set
    #     # without "missing" value
    #     with pytest.raises(colander.Invalid):
    #         inst.set_cstruct({})

    # def test_set_cstruct_non_valid_required_and_readonly(self):
    #     inst = self.make_one(DummyResource(), None, IPropertyB)
    #     inst.schema.children[0].required_ = True
    #     inst.schema.children[0].readonly = True
    #     with pytest.raises(AssertionError):
    #         inst.set_cstruct({})


class PoolPropertySheetUnitTest(unittest.TestCase):

    def make_one(self, *args):
        from . import PoolPropertySheetAdapter
        return PoolPropertySheetAdapter(*args)

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        from adhocracy.properties.interfaces import IPool
        from pyramid.httpexceptions import HTTPNotImplemented
        inst = self.make_one(DummyResource(), None, IPool)
        assert verifyObject(IResourcePropertySheet, inst) is True
        with pytest.raises(HTTPNotImplemented):
            inst.set_cstruct({})
        with pytest.raises(HTTPNotImplemented):
            inst.set({})

    def test_create_non_valid(self):
        with pytest.raises(AssertionError):
            self.make_one(DummyResource(), None, IPropertyB)

    def test_get_empty(self):
        from adhocracy.properties.interfaces import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = []
        inst = self.make_one(context, None, IPool)
        assert inst.get() == {"elements": []}

    def test_get_not_empty(self):
        from adhocracy.properties.interfaces import IPool
        context = make_folder_with_objectmap()
        context.__objectmap__.pathlookup.return_value = [1]
        context["child1"] = DummyResource()
        inst = self.make_one(context, None, IPool)
        assert inst.get() == {"elements": [1]}


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

    def test_register_ipropertysheet_adapter_inheritance(self):
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = DummyResource()
        inst_extend = self.make_one(self.config, context,
                                    DummyRequest(), IExtendPropertyB)
        assert IPropertyB.providedBy(context)
        assert IExtendPropertyB.providedBy(context)
        assert "count" in inst_extend.get()
        assert "newattribute" in inst_extend.get()

    def test_includeme_register_ipropertysheet_adapter_extend(self):
        self.register_propertysheet_adapter(self.config, IPropertyB)
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = DummyResource()
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

    def test_includeme_register_ipropertysheet_adapter_iname(self):
        from adhocracy.properties.interfaces import IName
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(), IName)
        assert inst.iface is IName

    def test_includeme_register_ipropertysheet_adapter_inamereadonly(self):
        from adhocracy.properties.interfaces import INameReadOnly
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(),
                             INameReadOnly)
        assert inst.iface is INameReadOnly

    def test_includeme_register_ipropertysheet_adapter_iversions(self):
        from adhocracy.properties.interfaces import IVersions
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(),
                             IVersions)
        assert inst.iface is IVersions

    def test_includeme_register_ipropertysheet_adapter_itags(self):
        from adhocracy.properties.interfaces import ITags
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(), ITags)
        assert inst.iface is ITags

    def test_includeme_register_ipropertysheet_adapter_iversionable(self):
        from adhocracy.properties.interfaces import IVersionable
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(),
                             IVersionable)
        assert inst.iface is IVersionable

    def test_includeme_register_ipropertysheet_adapter_ipool(self):
        from adhocracy.properties.interfaces import IPool
        from adhocracy.properties import PoolPropertySheetAdapter
        self.config.include("adhocracy.properties")
        inst = self.make_one(self.config, DummyResource(), DummyRequest(), IPool)
        assert isinstance(inst, PoolPropertySheetAdapter)
        assert inst.iface is IPool
