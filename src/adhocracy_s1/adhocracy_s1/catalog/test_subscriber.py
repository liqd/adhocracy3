from unittest.mock import call
from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from pyramid import testing


@fixture
def catalog():
    from substanced.interfaces import IService
    from substanced.interfaces import IFolder
    catalog = testing.DummyResource(__provides__=(IFolder, IService))
    catalog['adhocracy'] = testing.DummyResource(__provides__=(IFolder,
                                                               IService))
    catalog.reindex_index = Mock()
    return catalog


@fixture
def context(pool, catalog):
    pool['catalogs'] = catalog
    return pool


@fixture
def event(context):
    return testing.DummyResource(object=context)


class TestReindexDecistionDate:

    def call_fut(self, *args):
        from .subscriber import reindex_decision_date
        return reindex_decision_date(*args)

    def test_reindex_decision_date(self, event, catalog):
        from unittest.mock import call
        from .subscriber import reindex_decision_date
        from adhocracy_core.sheets.versions import IVersionable
        event.object['version'] = testing.DummyResource(__provides__=IVersionable)
        event.object['other'] = testing.DummyResource()
        reindex_decision_date(event)

        index_calls = catalog.reindex_index.call_args_list
        assert call(event.object, 'decision_date') in index_calls
        assert call(event.object['version'], 'decision_date') in index_calls
        assert call(event.object['other'], 'decistion_date') not in index_calls

    @mark.usefixtures('integration')
    def test_register_subscriber(self, registry):
        from . import subscriber
        handlers = [x.handler.__name__ for x in registry.registeredHandlers()]
        assert subscriber.reindex_decision_date.__name__ in handlers


