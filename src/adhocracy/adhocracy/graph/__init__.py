"""Utilities for working with the version/reference graph (DAG)."""

from adhocracy.interfaces import IResource
from adhocracy.interfaces import SheetReferenceType
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.utils import get_all_taggedvalues
from substanced.util import find_objectmap
from substanced.objectmap import ObjectMap


def _get_reftypes(objectmap, base_reftype=None, source_isheet=None):
    """Collect all used SheetReferenceTypes.

    Args:
        objectmap or None: the objectmap to consult, None value is allowed to
                           ease unit testing.
        base_reftype (SheetReferenceType, optional): Skip types that are not
                                                     subclasses of reftype.

        source_isheet (ISheet, optional): Skip types with a source isheet
                                          that is not a subclass of
                                          source_isheet.
    Returns:
        list of SheetReferenceTypes

    """
    reftypes = []
    if objectmap:
        for reftype in objectmap.get_reftypes():
            if isinstance(reftype, str):
                continue
            if not issubclass(reftype, SheetReferenceType):
                continue
            if base_reftype and not reftype.isOrExtends(base_reftype):
                continue
            if source_isheet:
                isheet = reftype.queryTaggedValue('source_isheet')
                if not isheet.isOrExtends(source_isheet):
                    continue
            reftypes.append(reftype)
    return reftypes


def _references_template(objectmap_method, context, source_isheet=None,
                         base_reftype=None):
    """ Template to get reference data with objectmap methods. """
    om = find_objectmap(context)
    reftypes = _get_reftypes(om, base_reftype, source_isheet)
    for reftype in reftypes:
        isheet = reftype.getTaggedValue('source_isheet')
        isheet_field = reftype.getTaggedValue('source_isheet_field')
        for resource in objectmap_method(om, context, reftype):
            yield (resource, isheet, isheet_field)


def get_back_references(resource):
    """Get references that point to this resource.

    Args:
        resource (IResource)
    Returns:
        list: tuples with the following content:
              referencing (IResource), isheet (ISheet), field_name (String)

    """
    return _references_template(ObjectMap.sources, resource)


def get_references(resource):
    """Get references of this resource pointing to other resources.

    Args:
        resource (IResource)
    Returns:
        list: tuples with the following content:
              referenced (IResource), isheet (ISheet), field_name (String)

    """
    return _references_template(ObjectMap.targets, resource)


def _get_fields(isheet):
    metadata = get_all_taggedvalues(isheet)
    fields = []
    for key, value in metadata.items():
        if key.startswith('field:'):
            name = key.split(':')[1]
            fields.append(name)
    return fields


def _build_dict_with_references_for_isheet(references, isheet):
    references_isheet = {}
    fieldnames = _get_fields(isheet)
    for resource, isheet, isheet_field in references:
        if isheet_field in fieldnames:
            # FIXME we return a list of resource here, but for big data a set
            # or generator would be much better
            resources = references_isheet.get(isheet_field, [])
            resources.append(resource)
            references_isheet[isheet_field] = resources
    return references_isheet


def get_references_for_isheet(resource, isheet):
    """ Get references of this resource pointing to others for one isheet only.

    Args:
        resource (IResource)
        isheet (ISheet)
    Returns:
        list: dicts with the following content:
              key - fieldname, value - referenced resrouces

              References from subtypes of isheet are also listed, if the
              field_name is part of the supertype.

    """
    references = _references_template(ObjectMap.targets, resource,
                                      source_isheet=isheet)
    return _build_dict_with_references_for_isheet(references, isheet)


def get_back_references_for_isheet(resource, isheet):
    """ Get references that point to this resource for one isheet only.

    Args:
        resource (IResource)
        isheet (ISheet)
    Returns:
        list: dicts with the following content:
              key - fieldname, value - referencing resources

              References from subtypes of isheet are also listed, if the
              field_name is part of the supertype.

    """
    references = _references_template(ObjectMap.sources, resource,
                                      source_isheet=isheet)
    return _build_dict_with_references_for_isheet(references, isheet)


def _get_targets(resource, base_reftype=SheetReferenceType):
    references = _references_template(ObjectMap.targets, resource,
                                      base_reftype=base_reftype)
    for reference in references:
        yield reference[0]


def _get_sources(resource, base_reftype=SheetReferenceType):
    references = _references_template(ObjectMap.sources, resource,
                                      base_reftype=base_reftype)
    for reference in references:
        yield reference[0]


def _is_candidate_ancestor(candidate, descendant, checked_candidates):
    """Return True if candidate is ancestor of descendant, False otherwise."""
    if candidate is descendant:
        return True
    checked_candidates.add(candidate.__oid__)

    children = _get_targets(candidate, base_reftype=SheetToSheet)
    unchecked_children = [x for x in children
                          if x.__oid__ not in checked_candidates]
    for child in unchecked_children:
        if _is_candidate_ancestor(child, descendant, checked_candidates):
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
    for candidate in ancestors:
        if _is_candidate_ancestor(candidate, descendant, set(),):
            return True
    return False


def get_follows(resource):
    """Determine the precessors ("follows") of a versionable resource.

    Args:
        resource (IResource)

    Returns:
        a iterator of precessor versions (possibly empty)

    """
    return _get_targets(resource, base_reftype=NewVersionToOldVersion)


def get_followed_by(resource):
        """Determine the successors ("followed_by") of a versionable resource.

        Args:
            resource (IResource)

        Returns:
            a generator of successor versions (possibly empty)

        """
        return _get_sources(resource, base_reftype=NewVersionToOldVersion)
