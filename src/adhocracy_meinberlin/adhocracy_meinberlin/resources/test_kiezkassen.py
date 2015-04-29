from pytest import mark
from pytest import fixture


@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.rate')
    config.include('adhocracy_core.resources.process')
    config.include('adhocracy_core.resources.asset')
    config.include('adhocracy_meinberlin.sheets.kiezkassen')
    config.include('adhocracy_meinberlin.resources.kiezkassen')


def test_proposal_meta():
    from .kiezkassen import proposal_meta
    from .kiezkassen import IProposalVersion
    assert proposal_meta.element_types == [IProposalVersion]
    assert proposal_meta.item_type == IProposalVersion
    # TODO assert proposal_meta.permission_add == 'add_kiezkassen_proposal'


@mark.usefixtures('integration')
def test_create_kiezkassen(registry, context):
    from adhocracy_meinberlin.resources.kiezkassen import IProposal
    assert registry.content.create(IProposal.__identifier__)


def test_kiezkassenversion_meta():
    from .kiezkassen import proposal_version_meta as meta
    from adhocracy_core.sheets.geo import IPoint
    from adhocracy_core.sheets.comment import ICommentable
    from adhocracy_core.sheets.rate import IRateable
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_core.sheets.description import IDescription
    from adhocracy_meinberlin.sheets.kiezkassen import IProposal
    assert meta.extended_sheets == [ITitle,
                                    IDescription,
                                    IProposal,
                                    IPoint,
                                    ICommentable,
                                    IRateable,
                                    ]
    assert meta.permission_add == 'add_kiezkassen_proposal_version'

@mark.usefixtures('integration')
def test_kiezkassenversion_create(registry):
    from adhocracy_meinberlin.resources.kiezkassen import IProposalVersion
    assert registry.content.create(IProposalVersion.__identifier__)


class TestProcess:

    @fixture
    def meta(self):
        from .kiezkassen import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources.process
        import adhocracy_core.sheets.image
        import adhocracy_meinberlin.sheets.kiezkassen
        from adhocracy_core.resources.asset import add_assets_service
        from .kiezkassen import IProcess
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(adhocracy_core.resources.process.IProcess)
        assert meta.is_implicit_addable is True
        assert meta.permission_add == 'add_kiezkassen_process'
        assert meta.extended_sheets == [
            adhocracy_meinberlin.sheets.kiezkassen.IWorkflowAssignment,
            adhocracy_core.sheets.geo.ILocationReference,
            adhocracy_core.sheets.image.IImageReference,
        ]
        assert add_assets_service in meta.after_creation


    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
