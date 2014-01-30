from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IISheet
from unittest.mock import call
from unittest.mock import patch
from pyramid import testing
from zope.interface import Interface
from zope.interface import taggedValue
from zope.interface import provider

import colander
import pytest
import unittest


############
#  helper  #
############


class InterfaceY(Interface):
    pass


@provider(IISheet)
class ISheetA(ISheet):
    taggedValue('schema', 'adhocracy.sheets.test_init.CountSchema')


@provider(IISheet)
class ISheetB(ISheet):
    taggedValue('schema', 'adhocracy.sheets.test_init.CountSchema')


@provider(IISheet)
class ISheetC(ISheet):
    taggedValue('schema', 'adhocracy.sheets.test_init.CountSchema')
    taggedValue('readonly', True)
    taggedValue('createmandatory', True)


class CountSchema(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


@provider(IISheet)
class ISheetZ(ISheet):
    taggedValue('schema',
                'adhocracy.sheets.test_init.CountSchemaMissingDefault')


class CountSchemaMissingDefault(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                missing=colander.drop)


@provider(IISheet)
class ISheetY(ISheet):
    taggedValue('schema',
                'adhocracy.sheets.test_init.CountSchemaMissingMissing')


class CountSchemaMissingMissing(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0)


@provider(IISheet)
class IExtendPropertyB(ISheetB):
    taggedValue('schema',
                'adhocracy.sheets.test_init.ExtendCountSchema')
    taggedValue('key', ISheetB.__identifier__)


class ExtendCountSchema(CountSchema):
    newattribute = colander.SchemaNode(colander.String(),
                                       default='',
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
        context = testing.DummyResource()
        iproperty = ISheetB
        inst = self.make_one(context, iproperty)
        assert inst.context == context
        assert inst.permission_view == 'view'
        assert inst.permission_edit == 'edit'
        assert inst.readonly is False
        assert inst.createmandatory is False
        assert isinstance(inst.schema, CountSchema)
        assert inst.key == ISheetB.__identifier__
        assert verifyObject(IResourcePropertySheet, inst) is True

    def test_create_non_valid_set_readonly_or_createmandatory(self):
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetC)

    def test_create_non_valid_non_mapping_context(self):
        with pytest.raises(AssertionError):
            self.make_one(object(), ISheetB)

    def test_create_non_valid_non_iproperty_iface(self):
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), InterfaceY)

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def test_create_references(self, dummy_reference_node=None):
        node = dummy_reference_node.return_value
        node.name = 'references'
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst.schema.children.append(node)
        assert inst._references == {'references': ISheetB.__identifier__
                                    + ':references'}

    def test_get_empty(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.get() == {'count': 0}

    def test_get_non_empty(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst._data['count'] = 11
        assert inst.get() == {'count': 11}

    def test_set_valid(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.set({'count': 11}) is True
        assert inst.get() == {'count': 11}

    def test_set_valid_empty(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.set({}) is False
        assert inst.get() == {'count': 0}

    def test_set_valid_omit_str(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.set({'count': 11}, omit='count') is False

    def test_set_valid_omit_tuple(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.set({'count': 11}, omit=('count',)) is False

    def test_set_valid_omit_wrong_key(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.set({'count': 11}, omit=('wrongkey',)) is True

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def _set_valid_references(self, old_oids, new_oids,
                              expected_connect_oids,
                              expected_disconnect_oids,
                              dummy_reference_node=None):

        node = dummy_reference_node.return_value
        node.name = 'references'
        node.deserialize.return_value = old_oids
        #default value
        node.serialize.return_value = []
        context = make_folder_with_objectmap()
        om = context.__objectmap__
        inst = self.make_one(context, ISheet)

        inst.schema.children.append(node)

        inst.set({'references': new_oids})
        reftype = inst._references['references']
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
        inst = self.make_one(testing.DummyResource(), ISheetB)
        assert inst.get_cstruct() == {'count': '0'}

    def test_get_cstruct_non_empty(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst._data['count'] = 11
        assert inst.get_cstruct() == {'count': '11'}

    def test_set_cstruct_valid(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst.set_cstruct({'count': '11'})
        assert inst.get_cstruct() == {'count': '11'}

    def test_set_cstruct_valid_empty(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst.set_cstruct({})
        assert inst.get_cstruct() == {'count': '0'}

    def test_set_cstruct_valid_with_name_conflicts(self):
        context = testing.DummyResource()
        inst1 = self.make_one(context, ISheetB)
        inst1.set_cstruct({'count': '1'})
        inst2 = self.make_one(context, ISheetA)
        inst2.set_cstruct({'count': '2'})
        assert inst1.get_cstruct() == {'count': '1'}
        assert inst2.get_cstruct() == {'count': '2'}

    def test_set_cstruct_valid_readonly(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        inst.schema.children[0].readonly = True
        inst.set_cstruct({'count': '1'})
        assert inst.get_cstruct() == {'count': '0'}

    def test_get_cstruct_non_valid_missing_default_value(self):
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetZ)

    def test_get_cstruct_non_valid_missing_missing_value(self):
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetY)

    def test_set_cstruct_non_valid_wrong_type(self):
        inst = self.make_one(testing.DummyResource(), ISheetB)
        with pytest.raises(colander.Invalid):
            inst.set_cstruct({'count': 'wrongnumber'})

    # TODO
    # def test_set_cstruct_non_valid_required(self):
    #     inst = self.make_one(DummyResource(), ISheetB)
    #     inst.schema.children[0].required_ = True
    #     # FIXME: the attriute required is automatically set
    #     # without 'missing' value
    #     with pytest.raises(colander.Invalid):
    #         inst.set_cstruct({})

    # def test_set_cstruct_non_valid_required_and_readonly(self):
    #     inst = self.make_one(DummyResource(), ISheetB)
    #     inst.schema.children[0].required_ = True
    #     inst.schema.children[0].readonly = True
    #     with pytest.raises(AssertionError):
    #         inst.set_cstruct({})


class ResourcePropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        inst = config.registry.getMultiAdapter((context, iface),
                                               IResourcePropertySheet)
        return inst

    def register_propertysheet_adapter(self, config, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.sheets import ResourcePropertySheetAdapter
        from zope.interface import Interface
        self.config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                             (iface, Interface),
                                             IResourcePropertySheet)

    def test_register_ipropertysheet_adapter_inheritance(self):
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = testing.DummyResource()
        inst_extend = self.get_one(self.config, context, IExtendPropertyB)
        assert ISheetB.providedBy(context)
        assert IExtendPropertyB.providedBy(context)
        assert 'count' in inst_extend.get()
        assert 'newattribute' in inst_extend.get()

    def test_register_ipropertysheet_adapter_extend(self):
        self.register_propertysheet_adapter(self.config, ISheetB)
        self.register_propertysheet_adapter(self.config, IExtendPropertyB)
        context = testing.DummyResource()
        inst_extend = self.get_one(self.config, context, IExtendPropertyB)
        inst = self.get_one(self.config, context, ISheetB)
        inst_extend.set({'count': 1})
        assert inst_extend.key == inst.key
        assert inst.get() == {'count': 1}
        assert inst_extend.get() == {'count': 1, 'newattribute': ''}
        inst.set({'count': 2})
        assert inst_extend.get() == {'count': 2, 'newattribute': ''}
        assert inst.get() == {'count': 2}

    def test_register_ipropertysheet_adapter_override(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.interfaces import IISheet
        from adhocracy.sheets import ResourcePropertySheetAdapter
        from zope.interface import Interface

        class OverrideAdapter(object):
            def __init__(*args):
                pass

        self.config.registry.registerAdapter(OverrideAdapter,
                                             (ISheetB, IISheet),
                                             IResourcePropertySheet)
        default_adapter = ResourcePropertySheetAdapter
        self.config.registry.registerAdapter(default_adapter,
                                             (ISheetB, Interface),
                                             IResourcePropertySheet)

        context = testing.DummyResource()
        inst = self.get_one(self.config, context, ISheetB)
        assert isinstance(inst, OverrideAdapter)
