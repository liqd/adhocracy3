from pyramid import testing
from pytest import fixture
from pytest import mark


class TestLogbook:

    @fixture
    def meta(self):
        from .logbook import logbook_service_meta
        return logbook_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from adhocracy_core import resources
        assert meta.iresource == resources.logbook.ILogbookService
        assert meta.iresource.isOrExtends(IServicePool)
        assert meta.content_name == 'logbook'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

    @mark.usefixtures('integration')
    def test_add_logbook_service(self, pool, registry):
        from substanced.util import find_service
        from .logbook import add_logbook_service
        add_logbook_service(pool, registry, {})
        assert find_service(pool, 'logbook')
