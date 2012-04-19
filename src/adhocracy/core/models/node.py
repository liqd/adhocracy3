from bulbs.model import Node
from bulbs.utils import initialize_elements
from zope.interface import implements

from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.interfaces import INode

from pyramid.threadlocal import get_current_registry

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
        g = self._get_graph()
        script = g.scripts.get('outV')
        params = dict(_id=self._id, label=label,
                      property_key=property_key, property_value=property_value)
        try:
            resp = g.client.gremlin(script, params)
        except SystemError as e:
            import json
            raise GremlinError("\n" + json.loads(e.message[1])["error"])
        #initialize node objects
        generator = initialize_elements(g.client, resp)

        return generator

    def inV(self, label=None, property_key=None, property_value=None):
        assert(bool(property_key) == bool(property_value)),\
                "You have to provide both property key and value or None"
        #send gremlin script
        g = self._get_graph()
        script = g.scripts.get('inV')
        params = dict(_id=self._id, label=label,
                      property_key=property_key, property_value=property_value)
        try:
            resp = g.client.gremlin(script, params)
        except SystemError as e:
            import json
            raise GremlinError("\n" + json.loads(e.message[1])["error"])
        #initialize node objects
        generator = initialize_elements(g.client, resp)

        return generator

class GremlinError(Exception):
    pass
