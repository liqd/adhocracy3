"""Utilities for working with the version/reference graph (DAG)."""

from adhocracy.interfaces import AdhocracyReferenceType
from substanced.objectmap import find_objectmap


def collect_reftypes(objectmap, excluded_fields = []):
    """Collect all Adhocracy reference types except those excluded.

    Args:
        objectmap: the objectmap to consult
        excluded_fields (optional list of strings): reference types with a
            source sheet field listed here will NOT be returned.

    Returns:
        All Adhocracy reference types except those mentioned in
        `excluded_fields`. For example, if ``excluded_fields = ['follows']``,
        all except the 'follows' relation will be returned.

    """
    result = []
    if excluded_fields is None:
        excluded_fields = []
    for reftype in objectmap.get_reftypes():
        if issubclass(reftype, AdhocracyReferenceType):
            fieldname = reftype.getTaggedValue('source_isheet_field')
            if fieldname not in excluded_fields:
                result.append(reftype)
    return result


def _check_ancestry(objectmap, reftypes, startnode, descendant,
       checked_children):
    """Helper method that recursively checks for an ancestry relation."""
    if startnode == descendant:
        return True  # Got it already!
    if startnode in checked_children:
        return False  # Node was already checked, no need to do it again

    checked_children.add(startnode)
    unchecked_children = set()

    # Check outgoing connections of the requested types
    for reftype in reftypes:
        for node in objectmap.targets(startnode, reftype):
            if node == descendant:
                return True  # Got it!
            if node not in checked_children and node not in unchecked_children:
                # We'll have to check this node
                unchecked_children.add(node)

    # Check any unchecked_children
    for node in unchecked_children:
        gotit = _check_ancestry(objectmap, reftypes, node, descendant,
                checked_children)
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
    if ancestor == descendant:
        return True

    objectmap = find_objectmap(ancestor)
    # We don't want no 'follows' links
    reftypes = collect_reftypes(objectmap, ['follows'])
    checked_children = set()
    return _check_ancestry(objectmap, reftypes, ancestor, descendant,
        checked_children)
