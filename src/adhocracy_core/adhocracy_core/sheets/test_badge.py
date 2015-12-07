from copy import deepcopy

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
from unittest.mock import Mock


class TestBadgeableSheet:

    @fixture
    def meta(self):
        from .badge import badgeable_meta
        return badgeable_meta

    @fixture
    def inst(self, pool, service, meta):
        pool['badge_assignments'] = service
        return meta.sheet_class(meta, pool)

    def test_meta(self, meta):
        from . import badge
        assert meta.isheet == badge.IBadgeable
        assert meta.schema_class == badge.BadgeableSchema
        assert meta.editable is False
        assert meta.creatable is False

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst, service ):
        assert inst.get() == {'post_pool': service,
                              'assignments': [],
                              }

    def test_get_back_reference(self, inst, sheet_catalogs, search_result):
        badge = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[badge])
        assert inst.get()['assignments'] == [badge]

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestCreateUniqueBadgeAssignmentValidator:

    def call_fut(self, badge, obj, kw):
        from .badge import create_unique_badge_assignment_validator
        return create_unique_badge_assignment_validator(badge, obj, kw)

    @fixture
    def context(self, pool, service, registry):
        pool.add_service('badge_assignments', service, registry=registry)
        return pool

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def node(self, node):
        node['badge'] = testing.DummyResource()
        node['object'] = testing.DummyResource()
        node['object2'] = testing.DummyResource()
        return node

    @fixture
    def request_(self, context):
        request = testing.DummyRequest()
        request.root = context
        return request

    @fixture
    def mock_find_service(self, monkeypatch):
        from . import badge
        mock = Mock()
        monkeypatch.setattr(badge, 'find_service', mock)
        return mock

    def test_raise_if_assignment_already_exists(self, node, context, registry,
                                                mock_sheet):
        import colander
        from .badge import IBadge
        from .badge import IBadgeAssignment
        badge = testing.DummyResource(__provides__=IBadge)
        mock_sheet.get.return_value = {'name': 'badge0',
                                       'badge': badge,
                                       'object': node['object']}
        registry.content.get_sheet.return_value = mock_sheet
        kw = {'registry': registry, 'context': context}
        validator = self.call_fut(node['badge'], node['object'], kw)
        assign0 = testing.DummyResource(__provides__=IBadgeAssignment)
        context['badge_assignments']['assign0'] = assign0
        with raises(colander.Invalid):
            validator(node, {'badge': badge,
                             'object': node['object']})

    def test_no_raise_if_updating(self, node, context, registry, mock_sheet):
        from .badge import IBadge
        from .badge import IBadgeAssignment
        badge = testing.DummyResource(__provides__=IBadge)
        mock_sheet.get.return_value = {'name': 'badge0',
                                       'badge': badge,
                                       'object': node['object']}
        registry.content.get_sheet.return_value = mock_sheet
        assign0 = testing.DummyResource(__provides__=IBadgeAssignment)
        kw = {'registry': registry, 'context': assign0}
        validator = self.call_fut(node['badge'], node['object'], kw)
        context['badge_assignments']['assign0'] = assign0
        assert validator(node, {'badge': badge,
                                'object': node['object']}) is None

    def test_raise_if_updating_but_result_in_same_badge(
            self, node, context, registry, mock_sheet, mock_find_service):
        import colander
        from .badge import IBadge
        from .badge import IBadgeAssignment
        mock_sheet_badge = deepcopy(mock_sheet)
        mock_sheet_name = deepcopy(mock_sheet)
        mock_sheet_badge2 = deepcopy(mock_sheet)
        mock_sheet_name2 = deepcopy(mock_sheet)
        badge = testing.DummyResource(__provides__=IBadge)
        mock_sheet_badge.get.return_value = {'badge': badge,
                                             'object': node['object']}
        mock_sheet_name.get.return_value = {'name': 'badge0'}
        mock_sheet_badge2.get.return_value = {'badge': badge,
                                              'object': node['object2']}
        mock_sheet_name2.get.return_value = {'name': 'badge0'}
        registry.content.get_sheet.side_effect = [mock_sheet_name,
                                                  mock_sheet_badge,
                                                  mock_sheet_name,
                                                  mock_sheet_badge2,
                                                  mock_sheet_name2,
                                                  ]
        assign0 = testing.DummyResource(__provides__=IBadgeAssignment)
        assign1 = testing.DummyResource(__provides__=IBadgeAssignment)
        context['badge_assignments']['assign0'] = assign0
        context['badge_assignments']['assign1'] = assign1
        mock_pool = Mock()
        mock_find_service.return_value = mock_pool
        mock_pool.values.return_value = [assign0, assign1]
        kw = {'registry': registry, 'context': assign0}
        validator = self.call_fut(node['badge'], node['object'], kw)
        with raises(colander.Invalid):
            validator(node, {'badge': badge,
                             'object': node['object2']})

    def test_no_raise_if_object_different(self, node, context,
                                          registry, mock_sheet):
        from .badge import IBadge
        from .badge import IBadgeAssignment
        badge = testing.DummyResource(__provides__=IBadge)
        mock_sheet.get.return_value = {'name': 'badge0',
                                       'badge': badge,
                                       'object': node['object']}
        registry.content.get_sheet.return_value = mock_sheet
        kw = {'registry': registry, 'context': context}
        validator = self.call_fut(node['badge'], node['object'], kw)
        assign0 = testing.DummyResource(__provides__=IBadgeAssignment)
        context['badge_assignments']['assign0'] = assign0
        assert validator(node, {'badge': badge,
                                'object': testing.DummyResource()}) is None

    def test_valid(self, node, context, registry, mock_sheet):
        from .badge import IBadge
        from .badge import IBadgeAssignment
        from copy import deepcopy
        mock_sheet2 = deepcopy(mock_sheet)
        mock_sheet3 = deepcopy(mock_sheet)
        mock_sheet.get.return_value = {'name': 'badge0'}
        badge = testing.DummyResource(__provides__=IBadge)
        mock_sheet2.get.return_value = {'badge': badge,
                                        'object': testing.DummyResource()}
        mock_sheet3.get.return_value = {'name': 'badge1'}
        registry.content.get_sheet.side_effect = [mock_sheet, mock_sheet2,
                                                  mock_sheet3]
        kw = {'registry': registry, 'context': context}
        validator = self.call_fut(node['badge'], node['object'], kw)
        assign0 = testing.DummyResource(__provides__=IBadgeAssignment)
        context['badge_assignments']['assign0'] = assign0
        assert validator(node, {'badge': badge,
                                'object': testing.DummyResource()}) is None


class TestBadgeAssignmentsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.badge import badge_assignment_meta
        return badge_assignment_meta

    @fixture
    def inst(self, context, meta):
        return meta.sheet_class(meta, context)

    @fixture
    def mock_create_post_validator(self, monkeypatch):
        from . import badge
        mock = Mock(spec=badge.create_post_pool_validator)
        monkeypatch.setattr(badge, 'create_post_pool_validator', mock)
        return mock

    @fixture
    def mock_create_assignment_validator(self, monkeypatch):
        from . import badge
        mock = Mock(spec=badge.create_unique_badge_assignment_validator)
        monkeypatch.setattr(badge, 'create_unique_badge_assignment_validator',
                            mock)
        return mock

    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
        from . import badge
        assert badge.IBadgeAssignment.extends(ISheetReferenceAutoUpdateMarker)
        assert meta.isheet == badge.IBadgeAssignment
        assert meta.schema_class == badge.BadgeAssignmentSchema
        assert meta.permission_edit == 'edit'

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst):
        assert inst.get() == {'subject': None,
                              'badge': None,
                              'object': None,
                              }

    def test_validate_object_post_pool(self, inst,
                                       mock_create_post_validator,
                                       mock_create_assignment_validator):
        inst.schema.validator(inst.schema, {})
        mock_create_post_validator.assert_called_with(inst.schema['object'],
                                                      {})
        mock_create_assignment_validator\
            .assert_called_with(inst.schema['badge'], inst.schema['object'], {})

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestBadgeSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.badge import badge_meta
        return badge_meta

    @fixture
    def inst(self, context, meta):
        return meta.sheet_class(meta, context)

    def test_meta(self, meta):
        from . import badge
        assert meta.isheet == badge.IBadge
        assert meta.schema_class == badge.BadgeSchema
        assert meta.permission_edit == 'edit'

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst):
        assert inst.get() == {'groups': []}

    def test_get_with_groups(self, inst):
        from adhocracy_core.resources.badge import IBadgeGroup
        group1 = testing.DummyResource(__provides__=IBadgeGroup,
                                       __name__='group1')
        group2 = testing.DummyResource(__provides__=IBadgeGroup)
        group1['group2'] = group2
        group2['badge'] = inst.context
        assert inst.get() == {'groups': [group2, group1]}

    def test_get_with_groups_no_context(self, meta):
        inst = meta.sheet_class(meta, None)
        assert inst.get() == {'groups': []}

    def test_get_with_groups_parent_not_badge_group(self, inst):
        from adhocracy_core.resources.badge import IBadgeGroup
        o1 = testing.DummyResource(__name__='o1')
        group2 = testing.DummyResource(__provides__=IBadgeGroup)
        o1['group2'] = group2
        group2['badge'] = inst.context
        assert inst.get() == {'groups': [group2]}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestHasBadgesPoolSheet:

    @fixture
    def meta(self):
        from .badge import has_badges_pool_meta
        return has_badges_pool_meta

    @fixture
    def inst(self, pool, service, meta):
        pool['badges'] = service
        return meta.sheet_class(meta, pool)

    def test_meta(self, meta):
        from . import badge
        assert meta.isheet == badge.IHasBadgesPool
        assert meta.schema_class == badge.HasBadgesPoolSchema
        assert meta.editable is False
        assert meta.creatable is False

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst, service ):
        assert inst.get() == {'badges_pool': service}

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestGetAssignableBadges:

    @fixture
    def mock_badges(self, service):
        return service

    @fixture
    def context(self, pool, mock_badges, mock_catalogs):
        pool['badges'] = mock_badges
        pool['catalogs'] = mock_catalogs
        return pool

    def call_fut(self, context, request):
        from .badge import get_assignable_badges
        return get_assignable_badges(context, request)

    def test_none_if_no_badges_services(self, request_):
        context_without_badges_service = testing.DummyResource()
        assert self.call_fut(context_without_badges_service, request_) == []

    def test_all_badges_inside_badges_service(
            self, mock_catalogs, search_result, query, mock_badges, context,
            request_):
        from .badge import IBadge
        badge = testing.DummyResource()
        mock_catalogs.search.return_value = search_result\
            ._replace(elements=[badge])
        assert self.call_fut(context, request_) == [badge]
        assert mock_catalogs.search.call_args[0][0] == query._replace(
            root=mock_badges,
            interfaces=IBadge,
            allows=(request_.effective_principals, 'assign_badge')
            )
