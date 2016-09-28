from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises

from adhocracy_core.resources.pool import IBasicPool


class TestFilteringPoolSheet:

    @fixture
    def registry(self, registry_with_content):
        registry_with_content.settings = {}
        return registry_with_content

    @fixture
    def meta(self):
        from adhocracy_core.sheets.pool import pool_meta
        return pool_meta

    @fixture
    def inst(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        return inst

    @fixture
    def inst_mock(self, inst, request_, registry):
        from adhocracy_core.interfaces import IResourceSheet
        inst.registry = registry
        inst.request = request_
        inst.get = Mock(spec=IResourceSheet.get)
        return inst

    def test_create(self, inst, meta):
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_core.sheets.pool import IPool
        from adhocracy_core.sheets.pool import PoolSchema
        from adhocracy_core.sheets.pool import PoolSheet
        from zope.interface.verify import verifyObject
        assert isinstance(inst, PoolSheet)
        assert verifyObject(IResourceSheet, inst)
        assert IResourceSheet.providedBy(inst)
        assert meta.schema_class == PoolSchema
        assert meta.isheet == IPool
        assert meta.editable is False
        assert meta.creatable is False

    def test_get_no_children(self, inst,  sheet_catalogs):
        appstruct = inst.get()
        assert sheet_catalogs.search.called is False
        assert appstruct == {'elements': [],
                             'frequency_of': {},
                             'group_by': {},
                             'count': 0,
                             }

    def test_get_with_children(self, inst, context,  sheet_catalogs):
        from adhocracy_core.interfaces import ISheet
        with_target_isheet = testing.DummyResource(__provides__=ISheet)
        context['child1'] = with_target_isheet
        without_target_isheet = testing.DummyResource()
        context['child2'] = without_target_isheet
        appstruct = inst.get()
        assert appstruct['elements'] == [with_target_isheet]
        assert appstruct['count'] == 1

    def test_get_custom_search(self, inst, sheet_catalogs, search_result):
        from adhocracy_core.interfaces import ISheet
        child = testing.DummyResource()
        sheet_catalogs.search.return_value = search_result._replace(
            elements=[child],
            count=1,
            frequency_of={'y': 1},
            group_by={'y': [child]})
        appstruct = inst.get({'indexes': {'tag': 'LAST'}})
        query = sheet_catalogs.search.call_args[0][0]
        assert query.root is inst.context
        assert query.depth == 1
        assert query.interfaces == ISheet  # default elements target isheet
        assert query.indexes == {'tag': 'LAST'}
        assert appstruct == {'elements': [child],
                             'frequency_of': {'y': 1},
                             'group_by': {'y': [child]},
                             'count': 1,
                             }

    def test_serialize(self, inst_mock):
        child = testing.DummyResource()
        inst_mock.get.return_value = {'elements': [child],
                                      'count': 1}
        cstruct = inst_mock.serialize(params={})
        assert cstruct == {'elements': [],
                           'count': '1'}

    def test_serialize_with_params(self, inst_mock, rest_url):
        child = testing.DummyResource()
        inst_mock.get.return_value = {'elements': [child],
                                      'count': 1}
        cstruct = inst_mock.serialize(params={'name': 'child'})
        assert cstruct == {'elements': [rest_url],
                           'count': '1'}

    def test_serialize_filter_by_view_permission(self, inst_mock):
        inst_mock.get = Mock()
        inst_mock.get.return_value = {'elements': []}
        cstruct = inst_mock.serialize()
        assert inst_mock.get.call_args[1]['params']['allows'] == \
            (inst_mock.request.effective_principals, 'view')

    def test_serialize_filter_by_view_permission_disabled(self, inst_mock):
        inst_mock.registry.settings['adhocracy.filter_by_view_permission'] = 'False'
        inst_mock.get = Mock()
        inst_mock.get.return_value = {}
        cstruct = inst_mock.serialize()
        assert 'allows' not in inst_mock.get.call_args[1]['params']

    def test_serialize_filter_by_only_visible(self, inst_mock):
        inst_mock.get.return_value = {'elements': []}
        cstruct = inst_mock.serialize()
        assert inst_mock.get.call_args[1]['params']['only_visible']

    def test_serialize_filter_by_only_visible_disabled(self, inst_mock):
        inst_mock.get.return_value = {}
        inst_mock.registry.settings['adhocracy.filter_by_visible'] = 'False'
        cstruct = inst_mock.serialize()
        assert 'only_visible' not in inst_mock.get.call_args[1]['params']

    def test_serialize_with_serialization_content(self, inst_mock, rest_url):
        child = testing.DummyResource()
        inst_mock.get.return_value = {'elements': [child]}
        cstruct = inst_mock.serialize(params={'serialization_form': 'content'})
        assert cstruct['elements'] == \
            [{'content_type': 'adhocracy_core.interfaces.IResource',
              'data': {},
              'path': rest_url}]

    def test_serialize_with_serialization_omit(self, inst_mock):
        child = testing.DummyResource()
        inst_mock.get.return_value = {'elements': [child]}
        cstruct = inst_mock.serialize(params={'serialization_form': 'omit'})
        assert cstruct['elements'] == []

    def test_serialize_with_show_count(self, inst_mock):
        inst_mock.get.return_value = {'count': 1}
        cstruct = inst_mock.serialize(params={'show_count': True})
        assert cstruct['count'] == '1'

    def test_serialize_with_show_aggregate(self, inst_mock):
        inst_mock.get.return_value = {'frequency_of': {'y': 1}}
        cstruct = inst_mock.serialize(params={'show_frequency': True,
                                              'frequency_of': 'index'})
        assert cstruct['aggregateby']['index'] == {'y': 1}



@mark.usefixtures('integration')
class TestIntegrationPoolSheet:

    @fixture
    def pool(self, pool_with_catalogs, registry):
        pool = self._make_resource(registry, parent=pool_with_catalogs,
                                   name='child')
        return pool

    def _make_resource(self, registry, parent=None, name='',
                       content_type=IBasicPool):
        from datetime import datetime
        from adhocracy_core.sheets.name import IName
        if name == '':
            name = datetime.now().isoformat()
        appstructs = {IName.__identifier__: {'name': name}}
        return registry.content.create(
            content_type.__identifier__, parent, appstructs)

    def _get_pool_sheet(self, pool, registry):
        from adhocracy_core.sheets.pool import IPool
        return registry.content.get_sheet(pool, IPool)

    def test_get_empty(self, pool, registry):
        inst = self._get_pool_sheet(pool, registry)
        assert inst.get() == {'elements': [],
                              'frequency_of': {},
                              'group_by': {},
                              'count': 0,
                              }

    def test_get_custom_search_empty(self, registry, pool):
        child = self._make_resource(registry, parent=pool, name='child')
        inst = self._get_pool_sheet(pool, registry)
        assert inst.get({'indexes': {'name':'WRONG'}})['elements'] == []

    def test_get_custom_search_not_empty(self, registry, pool):
        child = self._make_resource(registry, parent=pool, name='child')
        inst = self._get_pool_sheet(pool, registry)
        assert inst.get({'indexes': {'name':'child'}})['elements'] == [child]


@mark.usefixtures('integration')
def test_includeme_register_sheet(registry):
    from .pool import IPool
    context = testing.DummyResource(__provides__=IPool)
    assert registry.content.get_sheet(context, IPool)


