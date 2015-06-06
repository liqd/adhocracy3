from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
from unittest.mock import Mock


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.badge')


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
        from adhocracy_core.interfaces import IPostPoolSheet
        from adhocracy_core.schema import PostPoolMappingSchema
        from . import badge
        assert badge.IBadgeable.extends(IPostPoolSheet)
        assert meta.isheet == badge.IBadgeable
        assert meta.schema_class == badge.BadgeableSchema
        assert issubclass(meta.schema_class, PostPoolMappingSchema)
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


class TestBadgeAssignmentsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.badge import badge_assignment_meta
        return badge_assignment_meta

    @fixture
    def inst(self, context, meta):
        return meta.sheet_class(meta, context)

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
                              'object': None}

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

