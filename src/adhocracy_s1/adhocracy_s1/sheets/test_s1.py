import colander
from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


class TestWorkflowSheet:

    @fixture
    def meta(self):
        from .s1 import workflow_meta
        return workflow_meta

    def test_meta(self, meta):
        from . import s1
        assert meta.isheet == s1.IWorkflowAssignment
        assert meta.schema_class == s1.WorkflowAssignmentSchema
        assert meta.permission_edit == 'do_transition'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context, registry):
        workflow = registry.content.get_workflow('s1')
        inst = meta.sheet_class(meta, context)
        wanted =  {'propose': {},
                   'select': {},
                   'result': {},
                   'workflow': workflow,
                   'workflow_state': None}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)
