from pytest import fixture
from pytest import mark


class TestMercatorProposal:

    @fixture
    def meta(self):
        from .mercator import mercator_proposal_meta
        return mercator_proposal_meta

    def test_meta(self, meta):
        from adhocracy_mercator.resources import mercator
        from adhocracy_core.resources.comment import add_commentsservice
        from adhocracy_core.resources.rate import add_ratesservice
        from adhocracy_core.resources.logbook import add_logbook_service
        assert meta.iresource == mercator.IMercatorProposal
        assert meta.element_types == (mercator.IMercatorProposalVersion,
                                      mercator.IOrganizationInfo,
                                      mercator.IIntroduction,
                                      mercator.IDescription,
                                      mercator.ILocation,
                                      mercator.IStory,
                                      mercator.IOutcome,
                                      mercator.ISteps,
                                      mercator.IValue,
                                      mercator.IPartners,
                                      mercator.IFinance,
                                      mercator.IExperience,
                                      )
        assert meta.is_implicit_addable
        assert meta.item_type == mercator.IMercatorProposalVersion
        assert add_ratesservice in meta.after_creation
        assert add_commentsservice in meta.after_creation
        assert add_logbook_service in meta.after_creation
        assert meta.permission_create == 'create_mercator_proposal'

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        from adhocracy_core.sheets.name import IName
        appstructs = {
            IName.__identifier__ : {
                'name': 'dummy_proposal'
            }
        }
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      appstructs=appstructs)
        assert meta.iresource.providedBy(res)


class TestProposalVersion:

    @fixture
    def meta(self):
        from .mercator import mercator_proposal_version_meta
        return mercator_proposal_version_meta

    def test_meta(self, meta):
        from adhocracy_core.sheets.logbook import IHasLogbookPool
        from adhocracy_mercator.resources import mercator
        assert meta.iresource == mercator.IMercatorProposalVersion
        assert meta.permission_create == 'edit_mercator_proposal'
        assert IHasLogbookPool in meta.extended_sheets

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool)
        assert meta.iresource.providedBy(res)


class TestProcess:

    @fixture
    def meta(self):
        from .mercator import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources.process
        from adhocracy_core.resources.asset import add_assets_service
        from .mercator import IProcess
        from .mercator import IMercatorProposal
        import adhocracy_mercator.sheets.mercator
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(adhocracy_core.resources.process.IProcess)
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_process'
        assert meta.extended_sheets == (
            adhocracy_mercator.sheets.mercator.IWorkflowAssignment,
        )
        assert meta.element_types == (IMercatorProposal,)
        assert add_assets_service in meta.after_creation


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
