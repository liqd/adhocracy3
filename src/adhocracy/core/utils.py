
# collection of general convenience functions

def to_list(iterable):
    """
    Converts an iterable to a list::

    >>> from adhocracy.core.utils import to_list
    >>> to_list((1, 2, 3))
    [1, 2, 3]
    """
    return [x for x in iterable]
