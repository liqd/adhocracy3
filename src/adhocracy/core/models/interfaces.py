from zope.interface import Interface
from zope.interface import Attribute
from zope import schema


class IGraphConnection(Interface):
    """
    The graph connection object.
    Implementation based on http://bulbflow.com/docs/api/bulbs/base/graph/
    """

    vertices = Attribute("Object to create / search Vertices")

    edges = Attribute("Object to create / search edges ")

    adhocracyroot = Attribute("Proxy object to create / search AdhocracyRoot Nodes")

    container = Attribute("Proxy object to create / search Container Nodes")

    child = Attribute("Proxy object to create / search Child Relations")


class INode(Interface):
    """
    Graph node object.
    """
    name = schema.TextLine(title=u"node name (global UID)", required=True)


class IRelation(Interface):
    """
    Graph relation object.
    """
    label = schema.TextLine(title=u"relation type (predicate)", required=True)


class IAdhocracyRoot(INode):
    """
    Adhocracy root object.
    """
    pass


class IContainer(INode):
    """
    Container object.
    """
    text = schema.Text(title=u"test attribute")


class IChild(IRelation):
    """
    Object hierarchy relation.
    """
    label = schema.TextLine(title=u"FIXME child (relation type)",
                            required=True,
                            readonly=True)
    child_name = schema.TextLine(title=u"FIXME", required=True)

