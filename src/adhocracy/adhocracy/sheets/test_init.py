from unittest.mock import patch
import unittest

from pyramid import testing
from zope.interface.verify import verifyObject
import colander
import pytest

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import IResourceSheet


class ResourcePropertySheetUnitTests(unittest.TestCase):

    def make_one(self, *args):
        from adhocracy.sheets import GenericResourceSheet
        return GenericResourceSheet(*args)

    def setUp(self):
        from adhocracy.interfaces import sheet_metadata

        class SheetASchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        missing=colander.drop,
                                        default=0)

        class ISheetA(ISheet):
            pass

        self.metadata = sheet_metadata._replace(isheet=ISheetA,
                                                schema_class=SheetASchema,
                                                readable=True,
                                                editable=True,
                                                creatable=True)
        self.context = testing.DummyResource()

    def test_create_valid(self):
        inst = self.make_one(self.metadata, self.context)

        assert inst.context == self.context
        assert inst.meta == self.metadata
        assert isinstance(inst.schema, self.metadata.schema_class)
        assert inst._data_key == self.metadata.isheet.__identifier__
        assert verifyObject(IResourceSheet, inst) is True

    def test_get_empty(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.get() == {'count': 0}

    def test_get_non_empty(self):
        inst = self.make_one(self.metadata, self.context)
        inst._data['count'] = 11
        assert inst.get() == {'count': 11}

    def test_set_valid(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.set({'count': 11}) is True
        assert inst.get() == {'count': 11}

    def test_set_valid_empty(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.set({}) is False
        assert inst.get() == {'count': 0}

    def test_set_valid_omit_str(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.set({'count': 11}, omit='count') is False

    def test_set_valid_omit_tuple(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.set({'count': 11}, omit=('count',)) is False

    def test_set_valid_omit_wrong_key(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.set({'count': 11}, omit=('wrongkey',)) is True

    def test_set_valid_omit_readonly(self):
        inst = self.make_one(self.metadata, self.context)
        inst.schema['count'].readonly = True
        inst.set({'count': 11})
        assert inst.get() == {'count': 0}

    def test_set_valid_with_sheet_subtype_and_name_conflicts(self):
        sheet_a_meta = self.metadata

        class ISheetB(sheet_a_meta.isheet):
            pass

        class SheetBSchema(sheet_a_meta.schema_class):
            count = colander.SchemaNode(colander.Int(),
                                        missing=colander.drop,
                                        default=0)

        sheet_b_meta = sheet_a_meta._replace(isheet=ISheetB,
                                             schema_class=SheetBSchema)
        inst_a = self.make_one(sheet_a_meta, self.context)
        inst_b = self.make_one(sheet_b_meta, self.context)

        inst_a.set({'count': 1})
        inst_b.set({'count': 2})

        assert inst_a.get() == {'count': 1}
        assert inst_b.get() == {'count': 2}

    def test_get_cstruct_empty(self):
        inst = self.make_one(self.metadata, self.context)
        assert inst.get_cstruct() == {'count': '0'}

    def test_get_cstruct_non_empty(self):
        inst = self.make_one(self.metadata, self.context)
        inst._data['count'] = 11
        assert inst.get_cstruct() == {'count': '11'}

    @patch('adhocracy.graph.Graph')
    @patch('adhocracy.schema.ListOfUniqueReferences', autospec=True)
    def test_set_valid_references(self,
                                  dummy_node=None,
                                  dummy_graph=None):
        target = testing.DummyResource()
        node = dummy_node.return_value
        node.readonly = False
        node.name = 'references'
        inst = self.make_one(self.metadata, self.context)
        inst.schema.children.append(node)
        inst._graph = dummy_graph.return_value

        inst.set({'references': [target]})

        assert inst._graph.set_references.called
        assert inst._graph.set_references.call_args[0] \
            == (self.context, [target], node.reftype)


class ResourcePropertyIntegrationTests(unittest.TestCase):

    def _make_one(self, *args):
        from adhocracy.sheets import GenericResourceSheet
        return GenericResourceSheet(*args)

    def setUp(self):
        from adhocracy.sheets import sheet_metadata
        self.config = testing.setUp()
        self.context = testing.DummyResource()
        self.metadata = sheet_metadata._replace(isheet=ISheet,
                                                schema_class=colander.MappingSchema,
                                                readable=True,
                                                editable=True,
                                                creatable=True)

    def tearDown(self):
            testing.tearDown()

    def test_notify_resource_sheet_modified(self):
        from adhocracy.interfaces import IResourceSheetModified
        events = []
        listener = lambda event: events.append(event)
        self.config.add_subscriber(listener, IResourceSheetModified)
        inst = self._make_one(self.metadata, self.context)

        inst.set({'dummy': 'data'})

        assert IResourceSheetModified.providedBy(events[0])
        assert events[0].object == self.context

class AddSheetToRegistryIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.interfaces import sheet_metadata
        from adhocracy.interfaces import ISheet
        from adhocracy.sheets import GenericResourceSheet

        class SheetASchema(colander.MappingSchema):
            count = colander.SchemaNode(colander.Int(),
                                        missing=colander.drop,
                                        default=0)

        class ISheetA(ISheet):
            pass

        self.metadata = sheet_metadata._replace(isheet=ISheetA,
                                                sheet_class=GenericResourceSheet,
                                                schema_class=SheetASchema)
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, *args):
        from adhocracy.sheets import add_sheet_to_registry
        return add_sheet_to_registry(*args)

    def _get_one(self, context, isheet):
        registry = self.config.registry
        return registry.getAdapter(context,
                                   IResourceSheet,
                                   isheet.__identifier__)

    def test_register_valid_sheet_metadata(self):
        context = testing.DummyResource(__provides__=self.metadata.isheet)
        self._make_one(self.metadata, self.config.registry)

        sheet = self._get_one(context, self.metadata.isheet)

        assert self.metadata.isheet == sheet.meta.isheet

    def test_register_valid_sheet_metadata_replace_exiting(self):
        context = testing.DummyResource(__provides__=ISheet)
        metadata_a = self.metadata._replace(isheet=ISheet,
                                            permission_view='A')
        self._make_one(metadata_a, self.config.registry)
        metadata_b = self.metadata._replace(isheet=ISheet,
                                            permission_view='B')
        self._make_one(metadata_b, self.config.registry)

        sheet = self._get_one(context, ISheet)

        assert sheet.meta.permission_view == 'B'

    def test_register_non_valid_readonly_and_createmandatory(self):
        metadata = self.metadata._replace(editable=False,
                                          creatable=False,
                                          create_mandatory=True)
        with pytest.raises(AssertionError):
            self._make_one(metadata, self.config.registry)

    def test_register_non_valid_non_isheet(self):
        from zope.interface import Interface
        metadata = self.metadata._replace(isheet=Interface)
        with pytest.raises(AssertionError):
            self._make_one(metadata, self.config.registry)

    def test_register_non_valid_schema_without_default_values(self):
        del self.metadata.schema_class.__class_schema_nodes__[0].default
        with pytest.raises(AssertionError):
            self._make_one(self.metadata, self.config.registry)

    def test_register_non_valid_non_mapping_schema(self):
        metadata_a = self.metadata._replace(schema_class=colander.TupleSchema)
        with pytest.raises(AssertionError):
            self._make_one(metadata_a, self.config.registry)

    def test_register_non_valid_schema_subclass_has_changed_field_type(self):
        class SheetABSchema(self.metadata.schema_class):
            count = colander.SchemaNode(colander.String(),
                                        missing=colander.drop,
                                        default='D')

        class ISheetAB(self.metadata.isheet):
            pass

        metadata_b = self.metadata._replace(isheet=ISheetAB,
                                            schema_class=SheetABSchema)

        with pytest.raises(AssertionError):
            self._make_one(metadata_b, self.config.registry)


