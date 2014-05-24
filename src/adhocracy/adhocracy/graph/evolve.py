"""Evolution scripts."""
import logging

from adhocracy.graph import Graph


logger = logging.getLogger('evolution')


def add_graph_to_root_element(root):
    """Add the graph utility to the root object."""
    if not getattr(root, '__graph__', None):
        root.__graph__ = Graph(root)


def includeme(config):  # pragma: no cover
    """Graph package evolution steps."""
    config.add_evolution_step(add_graph_to_root_element)
