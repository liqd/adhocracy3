from zope.interface import Interface
from zope.interface import Attribute


class IGraphConnection(Interface):
    """The graph connection object.
       Implementation based on http://bulbflow.com/docs/api/bulbs/base/graph/
    """

    vertices = Attribute("Object to create / search Vertices")

    edges = Attribute("Object to create / search edges ")

    adhocracyroot = Attribute("Proxy object to create / search AdhocracyRoot Nodes")

    container = Attribute("Proxy object to create / search Container Nodes")

    child = Attribute("Proxy object to create / search Child Relations")


class IContainer(Interface):
    """The Container content
    """
