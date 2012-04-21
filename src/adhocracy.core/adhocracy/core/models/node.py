from bulbs.model import Node
from bulbs.utils import initialize_elements
from zope.interface import implements
from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.interfaces import INode
from adhocracy.core.utils import run_gremlin_script


class NodeAdhocracy(Node):


    implements(INode)

    def _get_graph(self):
        registry = get_current_registry()
        return registry.getUtility(IGraphConnection)

    def outV(self, label=None, property_key=None, property_value=None):
        """ read interface  """

        assert(bool(property_key) == bool(property_value)),\
                "You have to provide both property key and value or None"
        #send gremlin script
        graph = self._get_graph()
        params = dict(_id=self._id, label=label,
                      property_key=property_key, property_value=property_value)
        resp = run_gremlin_script(name='outV', params=params)
        #initialize node objects
        generator = initialize_elements(graph.client, resp)

        return generator

    def inV(self, label=None, property_key=None, property_value=None):
        assert(bool(property_key) == bool(property_value)),\
                "You have to provide both property key and value or None"
        #send gremlin script
        g = self._get_graph()
        params = dict(_id=self._id, label=label,
                      property_key=property_key, property_value=property_value)
        resp = run_gremlin_script(name='inV', params=params)
        #initialize node objects
        generator = initialize_elements(g.client, resp)

        return generator
