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
    config.include('adhocracy_meinberlin.workflows.bplan')
    config.include('adhocracy_meinberlin.sheets.bplan')


class TestProposalSheet:

    @fixture
    def meta(self):
        from .bplan import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import sheets
        assert meta.isheet == sheets.bplan.IProposal
        assert meta.schema_class == sheets.bplan.ProposalSchema

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'name': '',
                  'street_number': '',
                  'postal_code_city': '',
                  'email': '',
                  'statement': '',
                  }
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(registry, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestProposalSchema:

    @fixture
    def inst(self):
        from .bplan import ProposalSchema
        return ProposalSchema()

    def test_create(self, inst):
        import colander
        assert inst['name'].required
        assert inst['street_number'].required
        assert inst['postal_code_city'].required
        assert inst['email'].validator == colander.Email
        assert inst['statement'].required


class TestWorkflowSheet:

    @fixture
    def meta(self):
        from .bplan import workflow_meta
        return workflow_meta

    def test_meta(self, meta):
        from . import bplan
        assert meta.isheet == bplan.IWorkflowAssignment
        assert meta.schema_class == bplan.WorkflowAssignmentSchema
        assert meta.permission_edit == 'do_transition'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context, registry):
        bplan_workflow = registry.content.get_workflow('bplan')
        inst = meta.sheet_class(meta, context)
        wanted =  {'announce': {},
                   'draft': {},
                   'frozen': {},
                   'participate': {},
                   'workflow': bplan_workflow,
                   'workflow_state': None}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
