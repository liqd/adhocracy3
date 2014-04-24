"""Utilities for working with the version/reference graph (DAG)."""

from adhocracy.interfaces import IResource
from adhocracy.utils import get_reftypes
from adhocracy.sheets.versions import IVersionableFollowsReference
from substanced.objectmap import find_objectmap



def _check_ancestry(objectmap, reftypes, startnode, descendant, checked_map):
    """Helper method that recursively checks for an ancestry relation.

    checked_map is a mapping from object IDs to objects that have already been
    checked.

    Returns True if an ancestry relation was found, False otherwise.

    """
    startnode_oid = startnode.__oid__
    descendant_oid = descendant.__oid__
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


def is_in_subtree(descendant, ancestors):
    """Check wheter an resource is in a subtree below other resources.

    Args:
         descendant (IResource): the candidate descendant
         ancestors (list of IResource): the candidate ancestors

    Returns:
        True if there exists a relation from one of the `ancestors` to
        `descendant` that does NOT include any 'follows' links. For example,
        descendant might be an element of an element (of an element...) of an
        ancestor. Also if descendant and of the ancestors are the same node.

        False otherwise.

    """
    assert IResource.providedBy(descendant)
    assert isinstance(ancestors, list)

    result = False
    objectmap = find_objectmap(descendant)
    reftypes = collect_reftypes(objectmap, [IVersionableFollowsReference])

    checked_map = {}
    for ancestor in ancestors:
        if ancestor.__oid__ == descendant.__oid__:
            result = True
        else:
            result = _check_ancestry(objectmap, reftypes, ancestor, descendant,
                                     checked_map)
        if result:
            break

    return result
