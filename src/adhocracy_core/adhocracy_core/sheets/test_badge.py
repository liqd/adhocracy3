from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark


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
        pool['badges'] = service
        return meta.sheet_class(meta, pool)

    @fixture
    def test_meta(self, meta):
        from adhocracy_core.interfaces import IPostPoolSheet
        from adhocracy_core.schema import PostPoolMappingSchema
        from . import badge
        assert badge.IBadgeable.extends(IPostPoolSheet)
        assert meta.isheet == badge.IBadgeable
        assert isinstance(badge.BadgeableSchema, PostPoolMappingSchema)
        assert meta.schema_class == badge.BadgeableSchema
        assert meta.edit is False
        assert meta.create is False

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, inst, service ):
        assert inst.get() == {'post_pool': service,
                              'badged_by': [],
                              }

    def test_get_back_reference(self, inst, sheet_catalogs, search_result):
        badge = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[badge])
        assert inst.get()['badged_by'] == [badge]

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestBadgeAssignmentsSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.badge import badge_assignments_meta
        return badge_assignments_meta

    @fixture
    def inst(self, context, meta):
        return meta.sheet_class(meta, context)

    @fixture
    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
        from . import badge
        assert badge.IBadgeAssignments.extends(ISheetReferenceAutoUpdateMarker)
        assert meta.isheet == badge.IBadgeAssignments
        assert meta.schema_class == badge.BadgeAssignmentsSchema
        assert meta.edit_permission == 'edit_sheet_badge_assignments'

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'badges': []}

    def test_get_reference(self, inst, sheet_catalogs, search_result):
        badged = testing.DummyResource()
        sheet_catalogs.search.return_value =\
            search_result._replace(elements=[badged])
        assert inst.get()['badges'] == [badged]

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestBadgeDataSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.badge import badge_data_meta
        return badge_data_meta

    @fixture
    def inst(self, context, meta):
        return meta.sheet_class(meta, context)

    @fixture
    def test_meta(self, meta):
        from . import badge
        assert meta.isheet == badge.IBadgeData
        assert meta.schema_class == badge.BadgeDataSchema
        assert meta.edit_permission == 'edit_sheet_badge_data'

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'title': '',
                              'description': '',
                              'color': '',
                              }

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

    @fixture
    def test_meta(self, meta):
        from . import badge
        assert meta.isheet == badge.IHasBadgesPool
        assert meta.schema_class == badge.HasBadgesPoolSchema
        assert meta.edit is False
        assert meta.create is False

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

