"""Helper functions."""
from adhocracy.interfaces import IResource
from adhocracy.interfaces import ISheet
from functools import reduce
from zope.interface import Interface
from zope.interface import directlyProvidedBy
from zope.interface import providedBy

import copy
import colander
import json
import pprint


def create_schema_from_dict(key_values, base_node=None):
    """Create colander.SchemaNode instance from dictionary.

    Args:
         key_values (dict): Dictionary with colander schema names and nodes.
                            The key is the name and has to start with
                            "field:", has to be an instance of
                            colander.SchemaNode.

         base_node (colander.SchemaNode): Base Node to add the nodes to.
                                          Defaults to Mapping SchemaNode.
    Returns:
         colander.SchemaNode

    """
    if not base_node:
        base_node = colander.SchemaNode(colander.Mapping())
    for key, node in key_values.items():
        if not key.startswith('field:'):
            continue
        assert isinstance(node, colander.SchemaNode)
        name = key.split(':')[1]
        node.name = name
        base_node.add(node)
    return base_node


# def get_essence(context):
#     """Get resource essence.
#
#     Args:
#         context (IResource): object
#     Returns:
#         Set: context object and all objects in its ``essence``
#
#     """
#     assert IResource.providedBy(context)
#     essence = set()

def get_resource_interface(context):
    """Get resource type interface.

    Args:
        context (IResource): object
    Returns:
        Interface

    """
    assert IResource.providedBy(context)
    ifaces = list(directlyProvidedBy(context))
    iresources = [i for i in ifaces if i.isOrExtends(IResource)]
    return iresources[0]


def get_sheet_interfaces(context):
    """Get sheet interfaces.

    Args:
        context (IResource): object
    Returns:
        interfaces: list with ISheet interfaces

    """
    assert IResource.providedBy(context)
    ifaces = list(providedBy(context))
    return [i for i in ifaces if i.isOrExtends(ISheet)]


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


def diff_dict(old_dict, new_dict, omit=()):
    """Calculate changed keys of two dictionaries.

    Return tuple of (added, changed, removed) keys between old_dict and
    new_dict.

    """
    old = old_dict.keys() - set(omit)
    new = new_dict.keys() - set(omit)

    added = new - old
    removed = old - new

    common = old & new
    changed = set([key for key in common if old_dict[key] != new_dict[key]])

    return (added, changed, removed)


def sort_dict(d, sort_paths):
    """Return sorted dictionary."""
    d2 = copy.deepcopy(d)
    for path in sort_paths:
        base = reduce(lambda d, seg: d[seg], path[:-1], d2)
        base[path[-1]] = sorted(base[path[-1]])
    return d2


def pprint_json(json_dict):
    """Return sorted string representation of the dict."""
    json_dict_sorted = sort_dict(json_dict)
    py_dict = json.dumps(json_dict_sorted, sort_keys=True,
                         indent=4, separators=(',', ': '))
    pprint.pprint(py_dict)
