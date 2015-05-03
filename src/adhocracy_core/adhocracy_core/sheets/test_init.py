from unittest.mock import Mock

from pyramid import testing
from pytest import raises
from pytest import fixture
import colander


@fixture
def sheet_meta(sheet_meta):
    from adhocracy_core.sheets import AnnotationRessourceSheet
    from adhocracy_core.interfaces import ISheet
    class SheetASchema(colander.MappingSchema):
        count = colander.SchemaNode(colander.Int(),
            missing=colander.drop,
            default=0)
    meta = sheet_meta._replace(isheet=ISheet,
                               schema_class=SheetASchema,
                               sheet_class=AnnotationRessourceSheet,
                               readable=True,
                               editable=True,
                               creatable=True)
    return meta


class TestBaseResourceSheet:

    @fixture
    def request_(self):
        return testing.DummyRequest()

    @fixture
    def mock_node_unique_references(self):
        from adhocracy_core.schema import UniqueReferences
        from adhocracy_core.schema import SheetReference
        mock = Mock(spec=UniqueReferences)
        mock.readonly = False
        mock.name = 'references'
        mock.backref = False
        mock.reftype = SheetReference
        return mock

    @fixture
    def mock_node_single_reference(self):
        from adhocracy_core.schema import Reference
        from adhocracy_core.schema import SheetReference
        mock = Mock(spec=Reference)
        mock.readonly = False
        mock.name = 'reference'
        mock.backref = False
        mock.reftype = SheetReference
        return mock

    @fixture
    def context(self, context, mock_graph):
        context.__graph__ = mock_graph
        return context

    @fixture
    def inst(self, sheet_meta, context, registry):
        sheet_class = self.get_class()
        class DummyStorage(sheet_class):

            @property
            def _data(self):
                return context.__dict__

        inst = DummyStorage(sheet_meta, context, registry=registry)
        return inst

    def get_class(self):
        from adhocracy_core.sheets import BaseResourceSheet
        return BaseResourceSheet

    def test_create_valid(self, inst, sheet_meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert inst.context == context
        assert inst.meta == sheet_meta
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_create_valid_set_registry_if_available(self, sheet_meta, context,
                                                    registry):
        inst = self.get_class()(sheet_meta, context)
        assert inst.registry is registry

    def test_create_valid_set_registry_manually(self, sheet_meta, context):
        registry = testing.DummyResource()
        inst = self.get_class()(sheet_meta, context, registry=registry)
        assert inst.registry is registry

    def test_get_empty(self, inst):
        assert inst.get() == {'count': 0}

    def test_get_non_empty(self, inst):
        inst._data['count'] = 11
        assert inst.get() == {'count': 11}

    def test_get_with_custom_query(self, inst, sheet_catalogs,
                                   mock_node_unique_references):
        from adhocracy_core.interfaces import search_result
        node = mock_node_unique_references
        inst.schema.children.append(node)
        sheet_catalogs.search.return_value = search_result
        appstruct = inst.get({'depth': 100})
        query = sheet_catalogs.search.call_args[0][0]
        assert query.depth == 100

    def test_get_raise_if_query_key_is_no_search_query_key(self, inst):
        with raises(ValueError):
            inst.get({'WRONG': 100})

    def test_set_valid(self, inst):
        assert inst.set({'count': 11}) is True
        assert inst.get() == {'count': 11}

    def test_set_valid_empty(self, inst):
        assert inst.set({}) is False
        assert inst.get() == {'count': 0}

    def test_set_valid_omit_str(self, inst):
        assert inst.set({'count': 11}, omit='count') is False

    def test_set_valid_omit_tuple(self, inst):
        assert inst.set({'count': 11}, omit=('count',)) is False

    def test_set_valid_omit_wrong_key(self, inst):
        assert inst.set({'count': 11}, omit=('wrongkey',)) is True

    def test_set_valid_omit_readonly(self, inst):
        inst.schema['count'].readonly = True
        inst.set({'count': 11})
        assert inst.get() == {'count': 0}

    def test_set_valid_references(self, inst, context, mock_graph,
                                  mock_node_unique_references, registry):
        from adhocracy_core.interfaces import ISheet
        node = mock_node_unique_references
        inst.schema.children.append(node)
        inst.context._graph = mock_graph
        target = testing.DummyResource()

        inst.set({'references': [target]})

        mock_graph.set_references_for_isheet.assert_called_with(
            context, ISheet, {'references': [target]}, registry)

    def test_get_valid_back_references(self, inst, context, sheet_catalogs,
                                       mock_node_unique_references):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import search_result
        from adhocracy_core.interfaces import search_query
        from adhocracy_core.interfaces import Reference
        node = mock_node_unique_references
        node.backref = True
        inst.schema.children.append(node)
        source = testing.DummyResource()
        result = search_result._replace(elements=[source])
        sheet_catalogs.search.return_value = result

        appstruct = inst.get()

        reference = Reference(None, ISheet, '', context)
        query = search_query._replace(references=[reference],
                                      resolve=True,
                                      )
        sheet_catalogs.search.assert_called_with(query)
        assert appstruct['references'] == [source]

    def test_set_valid_reference(self, inst, context, mock_graph,
                                 mock_node_single_reference, registry):
        from adhocracy_core.interfaces import ISheet
        node = mock_node_single_reference
        inst.schema.children.append(node)
        target = testing.DummyResource()
        mock_graph.get_references_for_isheet.return_value = {}
        inst.set({'reference': target})
        graph_set_args = mock_graph.set_references_for_isheet.call_args[0]
        assert graph_set_args == (context, ISheet, {'reference': target}, registry)

    def test_get_valid_reference(self, inst, context, sheet_catalogs,
                                 mock_node_single_reference):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import search_result
        from adhocracy_core.interfaces import search_query
        from adhocracy_core.interfaces import Reference
        node = mock_node_single_reference
        inst.schema.children.append(node)
        target = testing.DummyResource()
        result = search_result._replace(elements=[target])
        sheet_catalogs.search.return_value = result

        appstruct = inst.get()

        reference = Reference(context, ISheet, 'reference', None)
        query = search_query._replace(references=[reference],
                                      resolve=True,
                                      )
        sheet_catalogs.search.assert_called_with(query)
        assert appstruct['reference'] == target

    def test_get_valid_back_reference(self, inst, context, sheet_catalogs,
                                      mock_node_single_reference):
        from adhocracy_core.interfaces import ISheet
        from adhocracy_core.interfaces import search_result
        from adhocracy_core.interfaces import Reference
        node = mock_node_single_reference
        node.backref = True
        inst.schema.children.append(node)
        source = testing.DummyResource()
        result = search_result._replace(elements=[source])
        sheet_catalogs.search.return_value = result
        appstruct = inst.get()

        reference = Reference(None, ISheet, '', context)
        assert sheet_catalogs.search.call_args[0][0].references == [reference]
        assert appstruct['reference'] == source

    def test_notify_resource_sheet_modified(self, inst, context, config):
        from adhocracy_core.interfaces import IResourceSheetModified
        from adhocracy_core.testing import create_event_listener
        events = create_event_listener(config, IResourceSheetModified)

        inst.set({'count': 2})

        assert IResourceSheetModified.providedBy(events[0])
        assert events[0].object == context
        assert events[0].registry == config.registry
        assert events[0].old_appstruct == {'count': 0}
        assert events[0].new_appstruct == {'count': 2}

    def test_get_cstruct(self, inst, request_):
        inst.set({'count': 2})
        assert inst.get_cstruct(request_) == {'count': '2'}

    def test_get_cstruct_with_params(self, inst, request_):
        inst.get = Mock()
        inst.get.return_value = {'elements': []}
        cstruct = inst.get_cstruct(request_, params={'name': 'child'})
        assert 'name' in inst.get.call_args[1]['params']

    def test_get_cstruct_filter_by_view_permission(self, inst, request_):
        inst.get = Mock()
        inst.get.return_value = {}
        cstruct = inst.get_cstruct(request_)
        assert inst.get.call_args[1]['params']['allows'] == \
               (request_.effective_principals, 'view')

    def test_get_cstruct_filter_by_only_visible(self, inst, request_):
        inst.get = Mock()
        inst.get.return_value = {}
        cstruct = inst.get_cstruct(request_)
        assert inst.get.call_args[1]['params']['only_visible']

    def test_delete_field_values_ignore_if_wrong_field(self, inst):
        inst._data['count'] = 2
        inst.delete_field_values(['count'])
        assert 'count' not in inst._data

    def test_delete_field_values(self, inst):
        inst._data['count'] = 2
        inst.delete_field_values(['wrong'])
        assert 'count' in inst._data


class TestAnnotationRessourceSheet:

    @fixture
    def sheet_meta(self, sheet_meta):
        from . import AnnotationRessourceSheet
        return sheet_meta._replace(sheet_class=AnnotationRessourceSheet)

    @fixture
    def inst(self, sheet_meta, context):
        from . import AnnotationRessourceSheet
        return AnnotationRessourceSheet(sheet_meta, context)

    def test_create(self, inst, context, sheet_meta):
        from . import BaseResourceSheet
        from adhocracy_core.interfaces import IResourceSheet
        from zope.interface.verify import verifyObject
        assert isinstance(inst, BaseResourceSheet)
        assert inst.context == context
        assert inst.meta == sheet_meta
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_set_valid_with_other_sheet_name_conflicts(self, inst, sheet_meta,
                                                       context):
        from adhocracy_core.interfaces import ISheet

        class ISheetB(ISheet):
            pass

        class SheetBSchema(sheet_meta.schema_class):
            count = colander.SchemaNode(colander.Int(),
                missing=colander.drop,
                default=0)

        sheet_b_meta = sheet_meta._replace(isheet=ISheetB,
                                           schema_class=SheetBSchema)
        inst_b = sheet_meta.sheet_class(sheet_b_meta, context)

        inst.set({'count': 1})
        inst_b.set({'count': 2})

        assert inst.get() == {'count': 1}
        assert inst_b.get() == {'count': 2}

    def test_set_valid_with_subtype_and_name_conflicts(self, inst,  sheet_meta,
                                                       context):
        class ISheetB(sheet_meta.isheet):
            pass

        class SheetBSchema(sheet_meta.schema_class):
            count = colander.SchemaNode(colander.Int(),
                missing=colander.drop,
                default=0)

        sheet_b_meta = sheet_meta._replace(isheet=ISheetB,
                                             schema_class=SheetBSchema)
        inst_b = sheet_meta.sheet_class(sheet_b_meta, context)

        inst.set({'count': 1})
        inst_b.set({'count': 2})

        assert inst.get() == {'count': 1}
        assert inst_b.get() == {'count': 2}


class TestAddSheetToRegistry:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def call_fut(self, sheet_meta, registry):
        from adhocracy_core.sheets import add_sheet_to_registry
        return add_sheet_to_registry(sheet_meta, registry)

    def test_register_valid_sheet_sheet_meta(self, sheet_meta, registry):
        self.call_fut(sheet_meta, registry)
        assert registry.content.sheets_meta == {sheet_meta.isheet: sheet_meta}

    def test_register_valid_sheet_sheet_meta_replace_exiting(self, sheet_meta,
                                                             registry):
        self.call_fut(sheet_meta, registry)
        meta_b = sheet_meta._replace(permission_view='META_B')
        self.call_fut(meta_b, registry)
        assert registry.content.sheets_meta == {sheet_meta.isheet: meta_b}

    def test_register_non_valid_readonly_and_createmandatory(self, sheet_meta, registry):
        meta = sheet_meta._replace(editable=False,
                                   creatable=False,
                                   create_mandatory=True)
        with raises(AssertionError):
            self.call_fut(meta, registry)

    def test_register_non_valid_non_isheet(self, sheet_meta, registry):
        from zope.interface import Interface
        meta = sheet_meta._replace(isheet=Interface)
        with raises(AssertionError):
            self.call_fut(meta, registry)

    def test_register_non_valid_schema_without_default_values(self, sheet_meta, registry):
        del sheet_meta.schema_class.__class_schema_nodes__[0].default
        with raises(AssertionError):
            self.call_fut(sheet_meta, registry)

    def test_register_non_valid_schema_with_default_colander_drop(self, sheet_meta, registry):
        sheet_meta.schema_class.__class_schema_nodes__[0].default = colander.drop
        with raises(AssertionError):
            self.call_fut(sheet_meta, registry)

    def test_register_non_valid_non_mapping_schema(self, sheet_meta, registry):
        meta = sheet_meta._replace(schema_class=colander.TupleSchema)
        with raises(AssertionError):
            self.call_fut(meta, registry)

    def test_register_non_valid_schema_subclass_has_changed_field_type(self, sheet_meta, registry):
        class SheetABSchema(sheet_meta.schema_class):
            count = colander.SchemaNode(colander.String(),
                missing=colander.drop,
                default='D')
        class ISheetAB(sheet_meta.isheet):
            pass
        meta_b = sheet_meta._replace(isheet=ISheetAB,
                                     schema_class=SheetABSchema)
        with raises(AssertionError):
            self.call_fut(meta_b, registry)
