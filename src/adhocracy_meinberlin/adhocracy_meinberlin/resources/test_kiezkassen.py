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
    config.include('adhocracy_meinberlin.sheets.kiezkassen')
    config.include('adhocracy_meinberlin.resources.kiezkassen')


def test_proposal_meta():
    from .kiezkassen import proposal_meta
    from .kiezkassen import IProposalVersion
    assert proposal_meta.element_types == [IProposalVersion]
    assert proposal_meta.item_type == IProposalVersion


@mark.usefixtures('integration')
def test_create_kiezkassen(registry, context):
    from adhocracy_meinberlin.resources.kiezkassen import IProposal
    assert registry.content.create(IProposal.__identifier__)


def test_kiezkassenversion_meta():
    from .kiezkassen import proposal_version_meta
    from adhocracy_core.sheets.geo import IPoint
    from adhocracy_core.sheets.comment import ICommentable
    from adhocracy_core.sheets.rate import IRateable
    from adhocracy_meinberlin.sheets.kiezkassen import IProposal
    assert proposal_version_meta.extended_sheets == [IProposal,
                                                     IPoint,
                                                     ICommentable,
                                                     IRateable,
                                                     ]

@mark.usefixtures('integration')
def test_kiezkassenversion_create(registry):
    from adhocracy_meinberlin.resources.kiezkassen import IProposalVersion
    assert registry.content.create(IProposalVersion.__identifier__)
