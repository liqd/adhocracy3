from pytest import mark
from pytest import fixture


def test_service_meta():
    from .service import service_meta
    from .service import IBasicService
    import adhocracy_core.sheets
    meta = service_meta
    meta.content_name == 'Service'
    meta.iresource == IBasicService
    meta.basic_sheet = [adhocracy_core.sheets.pool.IPool,
                        adhocracy_core.sheets.metadata.IMetadata,
                        ]

@fixture
def integration(config):
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets.metadata')
    config.include('adhocracy_core.resources.service')


@mark.usefixtures('integration')
class TestService:

    @fixture
    def context(self, pool):
        return pool

    def test_create_service(self, context, registry):
        from adhocracy_core.resources.service import IBasicService
        from substanced.interfaces import IService
        res = registry.content.create(IBasicService.__identifier__, context)
        assert IService.providedBy(res)
        assert res.__is_service__
