from pytest import mark
from pytest import fixture


def test_service_meta():
    from .service import service_meta as meta
    from .service import IBasicService
    import adhocracy_core.sheets
    assert meta.content_name == 'service'
    assert meta.iresource == IBasicService
    assert meta.basic_sheets == [adhocracy_core.sheets.pool.IPool,
                                 adhocracy_core.sheets.metadata.IMetadata,
                                 ]
    assert meta.permission_create == 'create_service'

@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.resources.service')


@mark.usefixtures('integration')
class TestService:

    def test_create_service(self, pool, registry):
        from adhocracy_core.resources.service import IBasicService
        from substanced.interfaces import IService
        res = registry.content.create(IBasicService.__identifier__, pool)
        assert IService.providedBy(res)
        assert res.__is_service__
        assert pool['service']
