import colander
from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_spd.workflows')
    config.include('adhocracy_spd.sheets')


class TestWorkflowSheet:

    @fixture
    def meta(self):
        from .digital_leben import workflow_meta
        return workflow_meta

    def test_meta(self, meta):
        from . import digital_leben
        assert meta.isheet == digital_leben.IWorkflowAssignment
        assert meta.schema_class == digital_leben.WorkflowAssignmentSchema
        assert meta.permission_edit == 'do_transition'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context, registry):
        digital_leben_workflow = registry.content.get_workflow('digital_leben')
        inst = meta.sheet_class(meta, context)
        wanted =  {'draft': {},
                   'frozen': {},
                   'participate': {},
                   'result': {},
                   'workflow': digital_leben_workflow,
                   'workflow_state': None}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
