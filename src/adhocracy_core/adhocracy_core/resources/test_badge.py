from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from pytest import raises


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.badge')


class TestBadge:

    @fixture
    def meta(self):
        from .badge import badge_data_meta
        return badge_data_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IBadgeData
        assert meta.basic_sheets == [sheets.metadata.IMetadata,
                                     sheets.name.IName,
                                     sheets.badge.IBadgeData,
                                    ]
        assert meta.permission_create == 'create_badge_data'

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestBadgesService:

    @fixture
    def meta(self):
        from .badge import badges_service_meta
        return badges_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from adhocracy_core import resources
        assert resources.badge.IBadgesService.extends(IServicePool)
        assert meta.iresource is resources.badge.IBadgesService
        assert meta.element_types == [resources.badge.IBadgeData]
        assert meta.content_name == 'badges'
        assert meta.permission_create == 'create_service'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

    @mark.usefixtures('integration')
    def test_add_badge_assignments_service(self, pool, registry):
        from substanced.util import find_service
        from .badge import add_badges_service
        add_badges_service(pool, registry, {})
        assert find_service(pool, 'badges')


class TestBadgeAssignment:

    @fixture
    def meta(self):
        from .badge import badge_assignment_meta
        return badge_assignment_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IBadge
        assert meta.basic_sheets == [sheets.metadata.IMetadata,
                                     sheets.badge.IBadgeAssignment,
                                    ]
        assert meta.permission_create == 'create_badge_assignment'
        assert meta.use_autonaming
        assert meta.autonaming_prefix == ''

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestBadgeAssignmentsService:

    @fixture
    def meta(self):
        from .badge import badge_assignments_service_meta
        return badge_assignments_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from adhocracy_core import resources
        assert resources.badge.IBadgeAssignementsService.extends(IServicePool)
        assert meta.iresource is resources.badge.IBadgeAssignementsService
        assert meta.element_types == [resources.badge.IBadgeAssignment]
        assert meta.content_name == 'badge_assignments'
        assert meta.permission_create == 'create_service'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

    @mark.usefixtures('integration')
    def test_add_badge_assignments_service(self, pool, registry):
        from substanced.util import find_service
        from .badge import add_badge_assignments_service
        add_badge_assignments_service(pool, registry, {})
        assert find_service(pool, 'badge_assignments')
