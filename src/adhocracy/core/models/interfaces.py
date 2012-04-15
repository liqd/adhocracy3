from zope.interface import Interface
from zope.interface import Attribute
from zope import schema


class IGraphConnection(Interface):
    """
    The graph connection object.
    Implementation based on http://bulbflow.com/docs/api/bulbs/base/graph/
    """

    scripts = Attribute("Gremlin scripts to send database requests")

    vertices = Attribute("Object to create / search Vertices")

    edges = Attribute("Object to create / search edges ")

    adhocracyroot = Attribute("Proxy object to create / search AdhocracyRoot Nodes")

    container = Attribute("Proxy object to create / search Container Nodes")

    child = Attribute("Proxy object to create / search Child Relations")


class INode(Interface):
    """
    Graph node object.
    """

    def outE(label=None):
        """
        Returns the outgoing edges.
        """

    def inE(label=None):
        """
        Returns the incoming edges.
        """

    def outV(label=None, property_key=None, property_value=None):
        """
        Returns outgoing vertiges
            :param label: Optional edge label.
            :param property_key: Optional edge property key.
            :param property_value: Optional edge property value.
            :type *: str
            :rtype: Vertex generator
        """

    def inV(label=None):
        """
        Returns the in-adjacent vertices.
        """

    def save():
        """
        Saves changes in the database.
        """


class IRelation(Interface):
    """
    Graph relation object.
    """
    label = schema.TextLine(title=u"relation type (predicate)", required=True)


class IAdhocracyRoot(Interface):
    """
    Adhocracy root object.
    """
    name = schema.TextLine(title=u"node name (global UID)", required=True)


class IContainer(Interface):
    """
    Container object.
    """
    name = schema.TextLine(title=u"node name (global UID)", required=True)

    text = schema.Text(title=u"test attribute")


class IChild(Interface):
    """
    Object hierarchy relation.
    """
    label = schema.TextLine(title=u"FIXME child (relation type)",
                            required=True,
                            readonly=True)
    child_name = schema.TextLine(title=u"FIXME", required=True)

