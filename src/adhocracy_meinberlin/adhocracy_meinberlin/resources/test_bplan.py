from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_meinberlin.sheets.bplan')
    config.include('adhocracy_meinberlin.resources.bplan')


class TestProposal:

    @fixture
    def meta(self):
        from .bplan import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import resources
        from adhocracy_meinberlin import sheets
        assert meta.iresource == resources.bplan.IProposal
        assert meta.element_types == [resources.bplan.IProposalVersion]
        assert meta.item_type == resources.bplan.IProposalVersion
        assert meta.permission_create == 'create_proposal'
        assert meta.extended_sheets == [sheets.bplan.IPrivateWorkflowAssignment]

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestProposalVersion:

    @fixture
    def meta(self):
        from .bplan import proposal_version_meta
        return proposal_version_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource == resources.bplan.IProposalVersion
        assert meta.extended_sheets == \
               [sheets.bplan.IProposal,
               ]
        assert meta.permission_create == 'edit_proposal'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestProcess:

    @fixture
    def meta(self):
        from .bplan import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.process import IProcess
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource is resources.bplan.IProcess
        assert resources.bplan.IProcess.isOrExtends(IProcess)
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_process'
        assert meta.extended_sheets == [
            sheets.bplan.IWorkflowAssignment,
        ]
        assert meta.permission_create == 'create_process'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

