from zope.interface import (
    implements,
    Interface,
    )
from zope.component import adapts

from pyramid_adoptedtraversal.interfaces import IChildsDictLike


class ExampleChildsDictLikeAdapter(object):
    """Example Adapter to implement IChildsDictLike.
       It just proxies to the context object.
    """

    implements(IChildsDictLike)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def __getitem__(self, name):
        if self.context.next is None:
            raise KeyError(name)
        return self.context.next
