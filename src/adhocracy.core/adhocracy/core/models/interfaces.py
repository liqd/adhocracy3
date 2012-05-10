from zope.interface import Interface
from zope.interface import taggedValue
from zope import schema

from pyramid_adoptedtraversal.interfaces import IChildsDictLike


class ILocationAware(Interface):
     """Attributes needed to make the object hierachy work
        http://readthedocs.org/docs/pyramid/en/1.3-branch/narr/resources.html#location-aware-resources
     """

     #__parent__ = schema.Object(required=True,)

     __name__ = schema.TextLine(title=u"Identifier (url slug)", required=True,)

     __acl__ = schema.List(title=u"ACL Control list", required=True, readonly=True)


class IChildsDict(IChildsDictLike):
    """
    Dictionary to set and get child nodes
    """


class INode(Interface):
    """
    Graph node object.
    """

    name = schema.TextLine(title=u"node name (global UID)", required=True)

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


class IContainer(Interface):
    """
    Container object.
    """
    taggedValue('name', 'container')
    taggedValue('class', 'adhocracy.core.models.container.Container')

    text = schema.Text(title=u"test attribute")


class IChild(Interface):
    """
    Object hierarchy relation.
    """
    taggedValue('name', 'child')
    taggedValue('class', 'adhocracy.core.models.relations.Child')

    label = schema.TextLine(title=u"FIXME child (relation type)",
                            required=True,
                            readonly=True)
    child_name = schema.TextLine(title=u"FIXME", required=True)
