"""Helper functions."""
from zope.interface import Interface


def get_all_taggedvalues(iface):
    """return dict with all own and all inherited taggedvalues."""
    iro = [i for i in iface.__iro__]
    iro.reverse()
    taggedvalues = dict()
    for i in iro:
        for key in i.getTaggedValueTags():
            taggedvalues[key] = i.getTaggedValue(key)
    return taggedvalues


def get_ifaces_from_module(module, base=Interface, blacklist=[]):
    """return list with interface class objects in module.

    Note: inspect.isclass is not working with interfaces,
    so we have to do it manually

    """
    ifaces = []
    for key in dir(module):
        value = getattr(module, key)
        if value in blacklist + [base]:
            continue
        try:
            if issubclass(value, base):
                ifaces.append(value)
        except TypeError:
            continue
    return ifaces
