from pytest import fixture
from pytest import mark
from webtest import TestResponse


def test_meractor_proposal_meta():
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


def test_meractor_proposal_version_meta():
    from .mercator import mercator_proposal_version_meta
    from .mercator import IMercatorProposalVersion
    meta = mercator_proposal_version_meta
    assert meta.iresource == IMercatorProposalVersion


@fixture
def integration(config):
    config.include('adhocracy_core.registry')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.rate')
    config.include('adhocracy_mercator.sheets.mercator')
    config.include('adhocracy_mercator.resources.mercator')


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


@fixture(scope='class')
def app_contributor(app_contributor):
    app_contributor.base_path = '/mercator'
    return app_contributor


def _post_proposal_item(app_user, path='/',  name='') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposal
    from adhocracy_core.sheets.name import IName
    iresource = IMercatorProposal
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post(path, iresource, sheets_cstruct)
    return resp


@mark.functional
class TestMercatorProposalPermissionsContributor:

    def test_can_create_proposal_item(self, app_contributor):
        resp = _post_proposal_item(app_contributor, path='/', name='proposal1')
        assert resp.status_code == 200

    def test_can_create_proposal_version(self, app_contributor):
        from adhocracy_mercator.resources import mercator
        possible_types = mercator.mercator_proposal_meta.element_types
        postable_types = app_contributor.get_postable_types('/proposal1')
        assert set(postable_types) == set(possible_types)
