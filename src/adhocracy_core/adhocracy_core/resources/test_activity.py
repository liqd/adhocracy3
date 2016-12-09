from pytest import fixture
from pytest import mark

class TestActivity:

    @fixture
    def meta(self):
        from .activity import activity_meta
        return activity_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISimple
        from . import activity
        import adhocracy_core.sheets
        assert meta.iresource is activity.IActivity
        assert meta.iresource.isOrExtends(ISimple)
        assert meta.permission_create == 'create_activity'
        assert meta.autonaming_prefix == 'activity'
        assert meta.basic_sheets == \
               (adhocracy_core.sheets.metadata.IMetadata,
                adhocracy_core.sheets.activity.IActivity,
                )
        assert meta.use_autonaming == True

    @mark.usefixtures('integration')
    def test_create(self, registry):
        from .page import IPage
        res = registry.content.create(IPage.__identifier__)
        assert IPage.providedBy(res)


class TestActivityService:

    @fixture
    def meta(self):
        from .activity import activity_service_meta
        return activity_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from . import activity
        assert meta.iresource is activity.IActivityService
        assert meta.iresource.isOrExtends(IServicePool)
        assert meta.element_types == (activity.IActivity,)

    @mark.usefixtures('integration')
    def test_create(self, pool, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__, pool)

    @mark.usefixtures('integration')
    def test_add_activity_service(self, pool, registry, meta):
        from substanced.util import find_service
        from .activity import add_activiy_service
        add_activiy_service(pool, registry, {})
        assert find_service(pool, 'activity_stream')
