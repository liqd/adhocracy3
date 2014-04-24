"""Utilities for working with the version/reference graph (DAG)."""

from adhocracy.interfaces import IResource
from adhocracy.utils import get_reftypes
from adhocracy.sheets.versions import IVersionableFollowsReference
from substanced.objectmap import find_objectmap


def _check_if_candidate_is_ancestor(objectmap, reftypes, candidate, descendant,
                                    checked_candidates):
    """Return True if candidate is ancestor of descendant, False otherwise."""
    if candidate is descendant:
        return True

    checked_candidates.add(candidate)

    candidate_children_unchecked = set()
    for reftype in reftypes:
        children = set(objectmap.targetids(candidate, reftype))
        candidate_children_unchecked = children.difference(checked_candidates)

    for candidate_child in candidate_children_unchecked:
        if _check_if_candidate_is_ancestor(objectmap, reftypes,
                                           candidate_child,
                                           descendant,
                                           checked_candidates):
            return True

    return False


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

    objectmap = find_objectmap(descendant)
    reftypes = get_reftypes(objectmap,
                            excluded_types=[IVersionableFollowsReference])
    for candidate in ancestors:
        if _check_if_candidate_is_ancestor(objectmap, reftypes,
                                           candidate.__oid__,
                                           descendant.__oid__,
                                           set()):
            return True
    return False
