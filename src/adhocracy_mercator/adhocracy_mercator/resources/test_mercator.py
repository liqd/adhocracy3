from pytest import fixture
from pytest import mark


def test_mercator_proposal_meta():
    from .mercator import mercator_proposal_meta
    from .mercator import IMercatorProposal
    from .mercator import IMercatorProposalVersion
    from .mercator import IOrganizationInfo
    from .mercator import IIntroduction
    from .mercator import IDescription
    from .mercator import ILocation
    from .mercator import IStory
    from .mercator import IOutcome
    from .mercator import ISteps
    from .mercator import IValue
    from .mercator import IPartners
    from .mercator import IFinance
    from .mercator import IExperience
    from adhocracy_core.resources.comment import add_commentsservice
    from adhocracy_core.resources.rate import add_ratesservice
    meta = mercator_proposal_meta
    assert meta.iresource == IMercatorProposal
    assert meta.element_types == [IMercatorProposalVersion,
                                  IOrganizationInfo,
                                  IIntroduction,
                                  IDescription,
                                  ILocation,
                                  IStory,
                                  IOutcome,
                                  ISteps,
                                  IValue,
                                  IPartners,
                                  IFinance,
                                  IExperience,
                                  ]
    assert meta.is_implicit_addable
    assert meta.item_type == IMercatorProposalVersion
    assert add_ratesservice in meta.after_creation
    assert add_commentsservice in meta.after_creation
    assert meta.permission_create == 'create_proposal'


def test_mercator_proposal_version_meta():
    from .mercator import mercator_proposal_version_meta
    from .mercator import IMercatorProposalVersion
    meta = mercator_proposal_version_meta
    assert meta.iresource == IMercatorProposalVersion
    assert meta.permission_create == 'edit_proposal'
 

@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.graph')
    config.include('adhocracy_core.resources.geo')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.pool')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_core.resources.item')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.rate')
    config.include('adhocracy_mercator.sheets.mercator')
    config.include('adhocracy_mercator.resources.mercator')
    config.include('adhocracy_mercator.resources.subscriber')


@mark.usefixtures('integration')
class TestIncludemeIntegration:

    @fixture
    def context(self, pool):
        return pool

    def test_create_mercator_proposal(self, context, registry):
        from .mercator import IMercatorProposal
        from adhocracy_core.sheets.name import IName
        appstructs = {
            IName.__identifier__ : {
                'name': 'dummy_proposal'
            }
        }
        res = registry.content.create(IMercatorProposal.__identifier__,
                                      parent=context,
                                      appstructs=appstructs)
        assert IMercatorProposal.providedBy(res)

    def test_create_mercator_proposal_version(self, context, registry):
        from .mercator import IMercatorProposalVersion
        res = registry.content.create(IMercatorProposalVersion.__identifier__,
                                      parent=context,
                                      )
        assert IMercatorProposalVersion.providedBy(res)


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
        assert meta.extended_sheets == [
            adhocracy_mercator.sheets.mercator.IWorkflowAssignment
        ]
        assert meta.element_types == [IMercatorProposal]
        assert add_assets_service in meta.after_creation


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
