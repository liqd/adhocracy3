from pytest import fixture
from pytest import mark
from webtest import TestResponse


# FIXME: move _create_proposal to somewhere in backend fixtures as the
# natural dependency ordering is "frontend depends on backend"
from mercator.tests.fixtures.fixturesMercatorProposals1 \
        import _create_proposal


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


def test_mercator_proposal_version_meta():
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


@fixture(scope='class')
def app_god(app_god):
    app_god.base_path = '/mercator'
    return app_god


def _post_proposal_item(app_user, path='/',  name='') -> TestResponse:
    from adhocracy_mercator.resources.mercator import IMercatorProposal
    from adhocracy_core.sheets.name import IName
    iresource = IMercatorProposal
    sheets_cstruct = {IName.__identifier__: {'name': name}}
    resp = app_user.post(path, iresource, sheets_cstruct)
    return resp


def _batch_post_full_sample_proposal(app_user) -> TestResponse:
    subrequests = _create_proposal()
    resp = app_user.batch(subrequests)
    return resp


@mark.functional
class TestMercatorProposalPermissionsAnonymous:

    def test_cannot_create_proposal_item(self, app_anonymous):
        resp = _post_proposal_item(app_anonymous, path='/', name='proposal1')
        assert resp.status_code == 403

    def test_cannot_create_proposal_per_batch(self, app_anonymous):
        resp = _batch_post_full_sample_proposal(app_anonymous)
        assert resp.status_code == 403

    def test_cannot_create_proposal_per_batch_broken_token(
            self, app_broken_token):
        resp = _batch_post_full_sample_proposal(app_broken_token)
        assert resp.status_code == 403


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

    def test_can_create_proposal_per_batch(self, app_contributor):
        resp = _batch_post_full_sample_proposal(app_contributor)
        assert resp.status_code == 200

    def test_cannot_create_other_users_proposal_version(self, app_contributor,
                                                        app_god):
        _post_proposal_item(app_god, path='/', name='proposal_other')
        postable_types = app_contributor.get_postable_types('/proposal_other')
        assert postable_types == []

    def test_non_god_creator_is_set(self, app_contributor):
        """Regression test issue #362"""
        from adhocracy_core.sheets.metadata import IMetadata
        resp = app_contributor.get('/proposal1')
        creator = resp.json['data'][IMetadata.__identifier__]['creator']
        assert '0000003' in creator

    def test_god_can_create_proposal_item(self, app_god):
        """Regression test issue #362"""
        resp = _post_proposal_item(app_god, path='/', name='god1')
        assert resp.status_code == 200

    def test_god_creator_is_set(self, app_god):
        """Regression test issue #362"""
        from adhocracy_core.sheets.metadata import IMetadata
        resp = app_god.get('/god1')
        creator = resp.json['data'][IMetadata.__identifier__]['creator']
        assert '0000000' in creator
