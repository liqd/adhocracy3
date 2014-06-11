import unittest

from pyramid import testing


class EvolveUnitTest(unittest.TestCase):

    def test_add_graph_to_root_element(self):
        from adhocracy.graph import Graph
        from adhocracy.graph.evolve import add_graph_to_root_element
        from adhocracy.utils import find_graph
        root = testing.DummyResource()

        add_graph_to_root_element(root)

        graph = find_graph(root)
        assert isinstance(graph, Graph)


    def test_add_graph_to_root_element_graph_already_exists(self):
        from adhocracy.graph import Graph
        from adhocracy.graph.evolve import add_graph_to_root_element
        from adhocracy.utils import find_graph
        root = testing.DummyResource()
        root.__graph__ = Graph(root)

        add_graph_to_root_element(root)

        graph = find_graph(root)
        assert isinstance(graph, Graph)


class EvolveIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_include_me(self):
        from substanced.interfaces import IEvolutionSteps
        self.config.include('substanced.evolution')
        self.config.include('adhocracy.graph')
        steps = self.config.registry.getUtility(IEvolutionSteps)
        assert 'adhocracy.graph.evolve.add_graph_to_root_element' in steps.names