"""Helper functions."""
from functools import reduce
import copy
import json
import pprint

from pyramid.compat import is_nonstr_iter
from substanced.util import get_dotted_name
from substanced.util import acquire
from zope.component import getAdapter
from zope.interface import directlyProvidedBy
from zope.interface import providedBy
from zope.interface.interfaces import IInterface

from adhocracy.interfaces import IResource
from adhocracy.interfaces import IResourceSheet
from adhocracy.interfaces import ISheet


def find_graph(context) -> object:
    """Get the Graph object in the lineage of `context` or None.

    :rtype: :class:`adhocracy.graph.Graph`

    """
    return acquire(context, '__graph__', None)


def get_iresource(context) -> IInterface:
    """Get the :class:`adhocracy.interfaces.IResource` interface or None."""
    ifaces = list(directlyProvidedBy(context))
    iresources = [i for i in ifaces if i.isOrExtends(IResource)]
    return iresources[0] if iresources else None


def get_isheets(context) -> [IInterface]:
    """Get the :class:`adhocracy.interfaces.ISheet` interfaces of `context`."""
    ifaces = list(providedBy(context))
    return [i for i in ifaces if i.isOrExtends(ISheet)]


def get_sheet(context, isheet: IInterface) -> IResourceSheet:
    """Get sheet adapter for the `isheet` interface.

    :raises: `zope.component.ComponentLookupError`

    """
    return getAdapter(context, IResourceSheet, name=isheet.__identifier__)


def get_all_sheets(context) -> [IResourceSheet]:
    """Get the sheet adapters for all ISheet interfaces of `context`.

    :rtype: :class:`types.GeneratorType`
    :raises: `zope.component.ComponentLookupError`

    """
    isheets = get_isheets(context)
    for isheet in isheets:
        yield(get_sheet(context, isheet))


def get_all_taggedvalues(iface: IInterface) -> dict:
    """Get dict with all own and all inherited taggedvalues."""
    iro = [i for i in iface.__iro__]
    iro.reverse()
    taggedvalues = {}
    for i in iro:
        for key in i.getTaggedValueTags():
            taggedvalues[key] = i.getTaggedValue(key)
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


def to_dotted_name(context) -> str:
    """Get the dotted name of `context`.

    :returns:
        The dotted name of `context`, if it's a type.  If `context` is a string
        it is returned as is (since we suppose that it already
        represents a type name).

    """
    if isinstance(context, str):
        return context
    else:
        return get_dotted_name(context)


def remove_keys_from_dict(dictionary: dict, keys_to_remove=()) -> dict:
    """Remove keys from `dictionary`.

    :param keys_to_remove: Tuple with keys or one key

    """
    if not is_nonstr_iter(keys_to_remove):
        keys_to_remove = (keys_to_remove,)
    dictionary_copy = {}
    for key, value in dictionary.items():
        if key not in keys_to_remove:
            dictionary_copy[key] = value
    return dictionary_copy
