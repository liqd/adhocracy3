import colander
from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_meinberlin.sheets.kiezkassen')


@mark.usefixtures('integration')
class TestIncludeme:

    def test_includeme_register_main_sheet(self, config):
        from .kiezkassen import IMain
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IMain)
        assert get_sheet(context, IMain)


class TestMainSheet:

    @fixture
    def meta(self):
        from .kiezkassen import main_meta
        return main_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from .kiezkassen import IMain
        from .kiezkassen import MainSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IMain
        assert inst.meta.schema_class == MainSchema

    def test_get_empty(self, meta, context):
        from decimal import Decimal
        inst = meta.sheet_class(meta, context)
        wanted = {'title': '',
                  'detail': '',
                  'budget': Decimal(0),
                  'creator_participate': False,
                  'location_text': '',
                  }
        assert inst.get() == wanted


class TestMainSchema:

    @fixture
    def inst(self):
        from .kiezkassen import MainSchema
        return MainSchema()

    @fixture
    def cstruct_required(self):
        return {'title': 'My title',
                'detail': 'My detail',
                'budget': '100.00',
                'creator_participate': True,
                'location_text': 'My location',
                }
