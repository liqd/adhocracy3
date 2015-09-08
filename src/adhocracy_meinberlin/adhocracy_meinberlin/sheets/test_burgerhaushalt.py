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
    config.include('adhocracy_meinberlin.workflows')
    config.include('adhocracy_meinberlin.sheets')


@mark.usefixtures('integration')
def test_includeme_register_proposal_sheet(config):
    from .burgerhaushalt import IProposal
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IProposal)
    assert get_sheet(context, IProposal)


class TestProposalSheet:

    @fixture
    def meta(self):
        from .burgerhaushalt import proposal_meta
        return proposal_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from .burgerhaushalt import IProposal
        from .burgerhaushalt import ProposalSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IProposal
        assert inst.meta.schema_class == ProposalSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'budget': None,
                  'location_text': '',
                  }
        assert inst.get() == wanted


class TestProposalSchema:

    @fixture
    def inst(self):
        from .burgerhaushalt import ProposalSchema
        return ProposalSchema()

    def test_create(self, inst):
        assert inst['budget'].validator.min == 0
        assert inst['budget'].required is False
        assert inst['location_text'].validator.max == 100

    def test_serialize_emtpy(self, inst):
        assert inst.serialize() == {'budget': None,
                                    'location_text': ''}

    def test_deserialize_emtpy(self, inst):
        assert inst.deserialize({}) == {}

    def test_deserialize_budget_none(self, inst):
        assert inst.deserialize({'budget': None}) == {}

    def test_deserialize_budget_positive_int(self, inst):
        from decimal import Decimal
        assert inst.deserialize({'budget': 1}) == {'budget': Decimal(1)}
