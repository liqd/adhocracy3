from pyramid import testing

import unittest


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import create_pool_with_graph
        config = testing.setUp()
        config.include('adhocracy.registry')
        config.include('adhocracy.events')
        config.include('adhocracy.sheets')
        config.include('adhocracy_sample.sheets.comment')
        config.include('adhocracy_sample.resources.proposal')
        self.config = config
        self.context = create_pool_with_graph()

    def tearDown(self):
        testing.tearDown()

    def test_includeme_registry_register_factories(self):
        from adhocracy_sample.resources.proposal import IProposalVersion
        from adhocracy_sample.resources.proposal import IProposal
        content_types = self.config.registry.content.factory_types
        assert IProposal.__identifier__ in content_types
        assert IProposalVersion.__identifier__ in content_types

    def test_includeme_registry_create_content(self):
        from adhocracy_sample.resources.proposal import IProposalVersion
        res = self.config.registry.content.create(IProposalVersion.__identifier__,
                                                  self.context)
        assert IProposalVersion.providedBy(res)
