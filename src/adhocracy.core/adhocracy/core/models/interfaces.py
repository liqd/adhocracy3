from zope import schema

from pyramid.interfaces import ILocation
from pyramid_adoptedtraversal.interfaces import IChildsDictLike

from adhocracy.dbgraph.interfaces import INode


class IChildsDict(IChildsDictLike):
    """
    Dictionary to set and get child nodes
    """


class ILocationAware(ILocation):
    """Attributes needed to make the object hierachy work
       http://readthedocs.org/docs/pyramid/en/1.3-branch/narr/resources.html\
       #location-aware-resources
    """

    __parent__ = schema.Object(schema=INode, readonly=True)

    __name__ = schema.TextLine(title=u"Identifier (url slug)", required=True,)

    __acl__ = schema.List(title=u"ACL Control list", required=True)
