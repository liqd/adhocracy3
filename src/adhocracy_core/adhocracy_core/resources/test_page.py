from pytest import fixture
from pytest import mark

class TestPage:

    @fixture
    def meta(self):
        from .page import page_meta
        return page_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import ISimple
        from . import page
        import adhocracy_core.sheets
        assert meta.iresource is page.IPage
        assert meta.iresource.isOrExtends(ISimple)
        assert meta.permission_create == 'create_page'
        assert meta.basic_sheets == \
               (adhocracy_core.sheets.name.IName,
                adhocracy_core.sheets.title.ITitle,
                adhocracy_core.sheets.description.IDescription,
                adhocracy_core.sheets.metadata.IMetadata,
                )
        assert meta.use_autonaming == False
        assert meta.is_sdi_addable == True

    @mark.usefixtures('integration')
    def test_create(self, registry):
        from .page import IPage
        res = registry.content.create(IPage.__identifier__)
        assert IPage.providedBy(res)


class TestPageService:

    @fixture
    def meta(self):
        from .page import page_service_meta
        return page_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from . import page
        assert meta.iresource is page.IPageService
        assert meta.iresource.isOrExtends(IServicePool)
        assert meta.element_types == (page.IPage,)

    @mark.usefixtures('integration')
    def test_create(self, pool, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__, pool)

    @mark.usefixtures('integration')
    def test_add_page_service(self, pool, registry, meta):
        from substanced.util import find_service
        from .page import add_page_service
        add_page_service(pool, registry, {})
        assert find_service(pool, 'pages')
