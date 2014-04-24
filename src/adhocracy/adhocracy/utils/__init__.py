"""Helper functions."""
from adhocracy.interfaces import IResource
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import AdhocracyReferenceType
from functools import reduce
from pyramid.path import DottedNameResolver
from substanced.util import get_dotted_name
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
    # accumulate tagged values
    for i in iro:
        for key in i.getTaggedValueTags():
            taggedvalues[key] = i.getTaggedValue(key)
    # normalise tagged values with python callables
    res = DottedNameResolver()
    for key, value in taggedvalues.items():
        if key in ['basic_sheets',
                   'extended_sheets',
                   'element_types',
                   'after_creation']:
            value_ = set([res.maybe_resolve(x) for x in value])
            taggedvalues[key] = value_
        if key in ['item_type',
                   'content_class']:
            value_ = res.maybe_resolve(value)
            taggedvalues[key] = value_
    return taggedvalues


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


def _sort_dict(d, sort_paths):  # pragma: no cover
    """Return sorted dictionary."""
    d2 = copy.deepcopy(d)
    for path in sort_paths:
        base = reduce(lambda d, seg: d[seg], path[:-1], d2)
        base[path[-1]] = sorted(base[path[-1]])
    return d2


def pprint_json(json_dict):  # pragma: no cover
    """Return sorted string representation of the dict.

    WARN: Not used and not testet

    """
    json_dict_sorted = _sort_dict(json_dict)
    py_dict = json.dumps(json_dict_sorted, sort_keys=True,
                         indent=4, separators=(',', ': '))
    pprint.pprint(py_dict)


def strip_optional_prefix(s, prefix):
    """Strip an optional prefix from a string.

    Args:
      s (str): the string to process
      prefix (str): the prefix to strip from the string, if present

    Returns:
      str: `s` stripped of the `prefix`

      If `s` doesn't start with `prefix`, it is returned unchanged.

    """
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s


def to_dotted_name(obj):
    """Return the dotted name of a type object.

    Args:
      obj (str or type)

    Returns:
      The dotted name of `obj`, if it's a type.
      If `obj` is a string, it is returned as is (since we suppose that it
      already represents a type name).

    """
    if isinstance(obj, str):
        return obj
    else:
        return get_dotted_name(obj)


def get_reftypes(objectmap, excluded_types=[]):
    """Helper function to collect all Adhocracy reference types excludes types.

    Args:
        objectmap: the objectmap to consult
        excluded_types (list of AdhocracyReferenceTypes, optional):
            reference types listed here will be skipped

    Returns:
        list of AdhocracyReferenceTypes

    """
    result = []
    for reftype in objectmap.get_reftypes():
        if isinstance(reftype, str):
            continue
        if not issubclass(reftype, AdhocracyReferenceType):
            continue
        if reftype in excluded_types:
            continue
        result.append(reftype)
    return result
