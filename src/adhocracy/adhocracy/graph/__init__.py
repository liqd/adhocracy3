"""Utilities for working with the version/reference graph (DAG)."""

from adhocracy.interfaces import AdhocracyReferenceType
from adhocracy.sheets.versions import IRootVersionsReference
from adhocracy.sheets.versions import IVersionableFollowsReference
from substanced.objectmap import find_objectmap


def collect_reftypes(objectmap, excluded_types=[]):
    """Collect all Adhocracy reference types except those excluded.

    Args:
        objectmap: the objectmap to consult
        excluded_types (optional list of types): reference types listed here
            will be skipped

    Returns:
        All Adhocracy reference types except those mentioned in
        `excluded_types`.

    """
    result = []
    if excluded_types is None:
        excluded_types = []
    for reftype in objectmap.get_reftypes():
        if issubclass(reftype, AdhocracyReferenceType):
            if reftype not in excluded_types:
                result.append(reftype)
    return result


def _check_ancestry(objectmap, reftypes, startnode, descendant, checked_map):
    """Helper method that recursively checks for an ancestry relation.

    checked_map is a mapping from object IDs to objects that have already been
    checked.

    Returns True if an ancestry relation was found, False otherwise.

    """
    startnode_oid = startnode.__oid__
    descendant_oid = descendant.__oid__

    if startnode_oid == descendant_oid:
        return True  # Got it already!
    if startnode_oid in checked_map:
        return False  # Node was already checked, no need to do it again

    checked_map[startnode_oid] = startnode
    unchecked_map = {}

    # Check outgoing connections of the requested types
    for reftype in reftypes:
        for node in objectmap.targets(startnode, reftype):
            node_oid = node.__oid__
            if node_oid == descendant_oid:
                return True  # Got it!
            if node_oid not in checked_map and node_oid not in unchecked_map:
                # We'll have to check this node
                unchecked_map[node_oid] = node

    # Check any unchecked_children
    for node in unchecked_map.values():
        gotit = _check_ancestry(objectmap, reftypes, node, descendant,
                                checked_map)
        if gotit:
            return True

    return False  # Sorry, not found


def is_ancestor(ancestor, descendant):
    """Check wheter an ancestry relation exists between two relations.

    Args:
         ancestor (IResource): the candidate ancestor
         descendant (IResource): the candidate descendant

    Returns:
        True iff there exists a relation from `ancestor` to `descendant` that
        does NOT include any 'follows' links. For example, descendant might be
        an element of an element (of an element...) of ancestor. Also if
        ancestor and descendant are the same node.

        False otherwise (including the case that ancestor or descendant is
        None).

    """
    if ancestor is None or descendant is None:
        return False
    if ancestor.__oid__ == descendant.__oid__:
        return True

    objectmap = find_objectmap(ancestor)
    # We don't want any 'follows' and 'root_versions' links
    reftypes = collect_reftypes(objectmap,
                                [IVersionableFollowsReference,
                                 IRootVersionsReference])
    checked_map = {}
    return _check_ancestry(objectmap, reftypes, ancestor, descendant,
                           checked_map)
