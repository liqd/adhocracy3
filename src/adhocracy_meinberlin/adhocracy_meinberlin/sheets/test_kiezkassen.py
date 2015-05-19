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
    config.include('adhocracy_meinberlin.workflows.kiezkassen')
    config.include('adhocracy_meinberlin.sheets.kiezkassen')


@mark.usefixtures('integration')
def test_includeme_register_proposal_sheet(config):
    from .kiezkassen import IProposal
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IProposal)
    assert get_sheet(context, IProposal)


class TestProposalSheet:

    @fixture
    def meta(self):
        from .kiezkassen import proposal_meta
        return proposal_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from .kiezkassen import IProposal
        from .kiezkassen import ProposalSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IProposal
        assert inst.meta.schema_class == ProposalSchema

    def test_get_empty(self, meta, context):
        from decimal import Decimal
        inst = meta.sheet_class(meta, context)
        wanted = {'budget': Decimal(0),
                  'creator_participate': False,
                  'location_text': '',
                  'address': '',
                  }
        assert inst.get() == wanted


class TestProposalSchema:

    @fixture
    def inst(self):
        from .kiezkassen import ProposalSchema
        return ProposalSchema()

    def test_create(self, inst):
        assert inst['budget'].validator.max == 50000
        assert inst['budget'].required
        assert inst['location_text'].validator.max == 100


class TestWorkflowSheet:

    @fixture
    def meta(self):
        from .kiezkassen import workflow_meta
        return workflow_meta

    def test_meta(self, meta):
        from . import kiezkassen
        assert meta.isheet == kiezkassen.IWorkflowAssignment
        assert meta.schema_class == kiezkassen.WorkflowAssignmentSchema
        assert meta.permission_edit == 'do_transition'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context, registry):
        kiezkassen_workflow = registry.content.get_workflow('kiezkassen')
        inst = meta.sheet_class(meta, context)
        wanted =  {'announce': {},
                   'draft': {},
                   'frozen': {},
                   'participate': {},
                   'result': {},
                   'workflow': kiezkassen_workflow,
                   'workflow_state': None}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
