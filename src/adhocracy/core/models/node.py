from bulbs.model import Node
from bulbs.utils import initialize_elements


from adhocracy.core.models.interfaces import IGraphConnection

from pyramid.threadlocal import get_current_registry

class NodeAdhocracy(Node):

    def _get_graph(self):
        registry = get_current_registry()
        return registry.getUtility(IGraphConnection)

    def outV(self, label=None, property_key=None, property_value=None):
        """
        Returns generator with initialized node objects

        :param label: Optional edge label.
        :param property_key: Optional edge property key.
        :param property_value: Optional edge property value.
        """
        assert(bool(property_key) == bool(property_value)),\
                "You have to provide both property key and value or None"
        #send gremlin script
        g = self._get_graph()
        script = g.scripts.get('outV')
        params = dict(_id=self._id, label=label,
                      property_key=property_key, property_value=property_value)
        resp = g.client.gremlin(script, params)
        #initialize node objects
        generator = initialize_elements(g.client, resp)

        return generator
