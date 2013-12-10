"""Helper functions."""
from functools import reduce
from zope.interface import Interface

import copy
import json
import pprint


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


def sort_dict(d, sort_paths):
    d2 = copy.deepcopy(d)
    for path in sort_paths:
        base = reduce(lambda d, seg: d[seg], path[:-1], d2)
        base[path[-1]] = sorted(base[path[-1]])
    return d2


def pprint_json(json_dict):
    json_dict_sorted = sort_dict(json_dict)
    py_dict = json.dumps(json_dict_sorted, sort_keys=True,
                         indent=4, separators=(',', ': '))
    pprint.pprint(py_dict)
