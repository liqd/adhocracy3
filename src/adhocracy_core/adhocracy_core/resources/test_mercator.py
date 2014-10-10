from pytest import fixture
from pytest import mark


@fixture
def integration(config):
    config.include('adhocracy_core.registry')
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets')
    config.include('adhocracy_core.sheets.mercator')
    config.include('adhocracy_core.resources.tag')
    config.include('adhocracy_core.resources.mercator')
    config.include('adhocracy_core.resources.comment')
    config.include('adhocracy_core.resources.rate')


@mark.usefixtures('integration')
class TestIncludemeIntegration:

    def test_includeme_registry_register_factories(self, config):
        from adhocracy_core.resources.mercator import IMercatorProposalVersion
        from adhocracy_core.resources.mercator import IMercatorProposal
        content_types = config.registry.content.factory_types
        assert IMercatorProposal.__identifier__ in content_types
        assert IMercatorProposalVersion.__identifier__ in content_types

    def test_includeme_registry_create_content(self,
                                               config,
                                               pool_graph_catalog):
        from adhocracy_core.resources.mercator import IMercatorProposal
        from adhocracy_core.sheets.name import IName
        appstructs = {
            IName.__identifier__ : {
                'name': 'dummy_proposal'
            }
        }
        res = config.registry.content.create(
            IMercatorProposal.__identifier__,
            parent=pool_graph_catalog,
            appstructs=appstructs)
        assert IMercatorProposal.providedBy(res)
