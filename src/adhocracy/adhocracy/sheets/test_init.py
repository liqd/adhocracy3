from adhocracy.interfaces import ISheet
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

    def setUp(self):
        class ISheetValid(ISheet):
            taggedValue('field:count',
                        colander.SchemaNode(colander.Int(),
                                            missing=colander.drop,
                                            default=0))
        self.isheet_valid = ISheetValid

    def test_create_valid(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from zope.interface.verify import verifyObject
        context = testing.DummyResource()
        isheet = self.isheet_valid
        inst = self.make_one(context, isheet)
        assert inst.context == context
        assert inst.permission_view == 'view'
        assert inst.permission_edit == 'edit'
        assert inst.readonly is False
        assert inst.createmandatory is False
        assert isinstance(inst.schema['count'], colander.SchemaNode)
        assert inst.key == isheet.__identifier__
        assert verifyObject(IResourcePropertySheet, inst) is True

    def test_create_non_valid_set_readonly_or_createmandatory(self):
        class ISheetA(ISheet):
            taggedValue('readonly', True)
            taggedValue('createmandatory', True)

        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetA)


    def test_create_non_valid_non_iproperty_iface(self):
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), Interface)

    def test_create_valid_missing_default_value(self):
        class ISheetA(ISheet):
            taggedValue('field:count',
                        colander.SchemaNode(colander.Int(),
                                            missing=colander.drop))
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetA)

    def test_create_non_valid_missing_missing_value(self):
        class ISheetA(ISheet):
            taggedValue('field:count',
                        colander.SchemaNode(colander.Int(),
                                            default=0))
        with pytest.raises(AssertionError):
            self.make_one(testing.DummyResource(), ISheetA)

    @patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
    def test_create_references(self, dummy_reference_node=None):
        from adhocracy.interfaces import SheetToSheet
        node = dummy_reference_node.return_value
        node.name = 'fieldname'
        node.reftype = SheetToSheet
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        inst.schema.children.append(node)
        assert inst._references == {'fieldname': SheetToSheet}

    def test_get_empty(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.get() == {'count': 0}

    def test_get_non_empty(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        inst._data['count'] = 11
        assert inst.get() == {'count': 11}

    def test_set_valid(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.set({'count': 11}) is True
        assert inst.get() == {'count': 11}

    def test_set_valid_empty(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.set({}) is False
        assert inst.get() == {'count': 0}

    def test_set_valid_omit_str(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.set({'count': 11}, omit='count') is False

    def test_set_valid_omit_tuple(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.set({'count': 11}, omit=('count',)) is False

    def test_set_valid_omit_wrong_key(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.set({'count': 11}, omit=('wrongkey',)) is True

    def test_set_valid_with_name_conflicts(self):
        class ISheetA(ISheet):
            taggedValue('field:count',
                        colander.SchemaNode(colander.Int(),
                                            missing=colander.drop,
                                            default=0))

        context = testing.DummyResource()

        inst1 = self.make_one(context, self.isheet_valid)
        inst1.set({'count': 1})
        inst2 = self.make_one(context, ISheetA)
        inst2.set({'count': 2})
        assert inst1.get() == {'count': 1}
        assert inst2.get() == {'count': 2}

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
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        assert inst.get_cstruct() == {'count': '0'}

    def test_get_cstruct_non_empty(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        inst._data['count'] = 11
        assert inst.get_cstruct() == {'count': '11'}

    def test_validate_cstruct_valid(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        appstruct = inst.validate_cstruct({'count': '11'})
        assert appstruct == {'count': 11}

    def test_validate_cstruct_valid_empty(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        appstruct = inst.validate_cstruct({})
        assert appstruct == {}

    def test_validate_cstruct_non_valid_readonly(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        inst.schema.children[0].readonly = True
        with pytest.raises(colander.Invalid):
            inst.validate_cstruct({'count': 1})

    def test_validate_cstruct_non_valid_wrong_type(self):
        inst = self.make_one(testing.DummyResource(), self.isheet_valid)
        with pytest.raises(colander.Invalid):
            inst.validate_cstruct({'count': 'wrongnumber'})


class ResourcePropertySheetAdapterIntegrationTest(unittest.TestCase):

    def setUp(self):
        class ISheetValid(ISheet):
            taggedValue('field:count',
                        colander.SchemaNode(colander.Int(),
                                            missing=colander.drop,
                                            default=0))
        self.isheet_valid = ISheetValid
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def get_one(self, config, context, iface):
        from adhocracy.utils import get_sheet
        from zope.interface import alsoProvides
        alsoProvides(context, iface)
        return get_sheet(context, iface)

    def register_propertysheet_adapter(self, config, iface):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.sheets import ResourcePropertySheetAdapter
        from zope.interface import Interface
        self.config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                             (iface, Interface),
                                             IResourcePropertySheet)

    def test_register_ipropertysheet_adapter_inheritance(self):
        class IExtendISheetValid(self.isheet_valid):
            taggedValue('field:new',
                        colander.SchemaNode(colander.String(),
                                            default='',
                                            missing=colander.drop))
            taggedValue('key', self.isheet_valid.__identifier__)

        self.register_propertysheet_adapter(self.config, IExtendISheetValid)
        context = testing.DummyResource()
        inst_extend = self.get_one(self.config, context, IExtendISheetValid)
        assert self.isheet_valid.providedBy(context)
        assert IExtendISheetValid.providedBy(context)
        assert 'count' in inst_extend.get()
        assert 'new' in inst_extend.get()

    def test_register_ipropertysheet_adapter_extend(self):
        class IExtendISheetValid(self.isheet_valid):
            taggedValue('field:new',
                        colander.SchemaNode(colander.String(),
                                            default='',
                                            missing=colander.drop))
            taggedValue('key', self.isheet_valid.__identifier__)

        self.register_propertysheet_adapter(self.config, self.isheet_valid)
        self.register_propertysheet_adapter(self.config, IExtendISheetValid)
        context = testing.DummyResource()
        inst_extend = self.get_one(self.config, context, IExtendISheetValid)
        inst = self.get_one(self.config, context, self.isheet_valid)
        inst_extend.set({'count': 1})
        assert inst_extend.key == inst.key
        assert inst.get() == {'count': 1}
        assert inst_extend.get() == {'count': 1, 'new': ''}
        inst.set({'count': 2})
        assert inst_extend.get() == {'count': 2, 'new': ''}
        assert inst.get() == {'count': 2}

    def test_register_ipropertysheet_adapter_override(self):
        from adhocracy.interfaces import IResourcePropertySheet
        from adhocracy.sheets import ResourcePropertySheetAdapter
        from zope.interface.interfaces import IInterface

        class IISpecialAdapter(IInterface):
            pass

        @provider(IISpecialAdapter)
        class ISheetValid(ISheet):
            pass

        class OverrideAdapter(object):
            def __init__(*args):
                pass

        self.config.registry.registerAdapter(OverrideAdapter,
                                             (ISheetValid, IISpecialAdapter),
                                             IResourcePropertySheet)
        default_adapter = ResourcePropertySheetAdapter
        self.config.registry.registerAdapter(default_adapter,
                                             (ISheetValid, IInterface),
                                             IResourcePropertySheet)

        context = testing.DummyResource()
        inst = self.get_one(self.config, context, ISheetValid)
        assert isinstance(inst, OverrideAdapter)
