from zope import interface
from zope import schema
from zope.component import adapts

from adhocracy.dbgraph.embeddedgraph import get_graph
from adhocracy.dbgraph.interfaces import IReference
from adhocracy.dbgraph.fieldproperty import AdoptedFieldProperty


class IChildMarker(IReference):
    """
    Object hierarchy reference marker interface
    """


class IChild(interface.Interface):
    """
    Object hierarchy reference.
    """

    child_name = schema.TextLine(title=u"child name", required=True)


class Child(object):
    interface.implements(IChild)
    adapts(IChildMarker)

    def __init__(self, context):
        self.context = context

    child_name = AdoptedFieldProperty(IChild["child_name"])


@interface.implementer(IChildMarker)
def child_factory(child, parent, child_name):
    graph = get_graph()
    content = graph.add_edge(child, parent, "child", \
                             main_interface=IChildMarker)
    content.set_property("child_name", child_name)
    return content
