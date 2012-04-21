from zope.interface import Interface


class IChildsDictLike(Interface):

    def __getitem__(child_key):
        """Get the object traversal child object"""
