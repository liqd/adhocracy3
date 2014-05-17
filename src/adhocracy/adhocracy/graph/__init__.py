"""Utilities for working with the version/reference graph (DAG)."""

from collections import Sequence
from collections import Iterable
from collections import namedtuple

from substanced.util import find_objectmap
from substanced.objectmap import ObjectMap
from substanced.objectmap import Multireference

from adhocracy.interfaces import IResource
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetReferenceType
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion
from adhocracy.utils import get_all_taggedvalues


class Reference(namedtuple('Reference', 'source isheet field target')):
    pass


def get_references(resource, base_isheet=ISheet, base_reftype=SheetToSheet):
    """Get generator with references of resource pointing to other resources.

    : return: generator of References
    """
    om = find_objectmap(resource)
    for isheet, field, reftype in _get_reftypes(om, base_isheet, base_reftype):
        for target in ObjectMap.targets(om, resource, reftype):
            yield Reference(resource, isheet, field, target)


def get_back_references(resource, base_isheet=ISheet,
                        base_reftype=SheetReferenceType):
    """Get generator with references of other resources pointing to resource.

    : return: generator of References
    """
    om = find_objectmap(resource)
    for isheet, field, reftype in _get_reftypes(om, base_isheet, base_reftype):
        for source in ObjectMap.sources(om, resource, reftype):
            yield Reference(source, isheet, field, resource)


_isheet_reftype = namedtuple('ISheetReftype', 'isheet field reftype')


def _get_reftypes(objectmap, base_isheet=ISheet,
                  base_reftype=SheetReferenceType) -> [_isheet_reftype]:
    """Collect all used SheetReferenceTypes.

    : parma objectmap: the objectmap to consult, None value is allowed to
                       ease unit testing.
    : param base_reftype: Skip types that are not subclasses of this.
    : param base_isheet: Skip types with a source isheet that is not a
                    subclass of this.
    """
    all_reftypes = objectmap.get_reftypes() if objectmap else []
    for reftype in all_reftypes:
        if isinstance(reftype, str):
            continue
        if not issubclass(reftype, SheetReferenceType):
            continue
        if not reftype.isOrExtends(base_reftype):
            continue
        isheet = reftype.queryTaggedValue('source_isheet')
        if not isheet.isOrExtends(base_isheet):
            continue
        field = reftype.queryTaggedValue('source_isheet_field')
        yield _isheet_reftype(isheet, field, reftype)


def set_references(resource, targets, reftype):
    """Set references of this resource pointing to other resources.

    : param targets (Iterable). the reference targets,
                                for Sequences the order is preserved.
    : param reftype: (SheetReferenceType):
    """
    assert resource is not None
    assert isinstance(targets, Iterable)
    assert issubclass(reftype, SheetReferenceType)

    ordered = isinstance(targets, Sequence)
    orientation = 'source'
    resolve = True  # return objects not oids
    ignore_missing = True  # don't raise ValueError if targets are missing
    om = find_objectmap(resource)
    multireference = Multireference(resource, om, reftype, ignore_missing,
                                    resolve, orientation, ordered)
    multireference.clear()
    multireference.connect(targets)


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
    references = get_references(resource, base_isheet=isheet)
    return _build_dict_with_references_for_isheet(references, isheet,
                                                  orientation='targets')


def get_back_references_for_isheet(resource, isheet):
    """ Get references that point to this resource for one isheet only.

    Args:
        resource (IResource):
        isheet (ISheet): references of tihs isheet and all subclasses
    Returns:
        list: dicts with the following content:
              key - fieldname, value - referencing resources

              References from subtypes of isheet are also listed, if the
              field_name is part of the supertype.

    """
    references = get_back_references(resource, base_isheet=isheet)
    return _build_dict_with_references_for_isheet(references, isheet,
                                                  orientation='sources')


def _build_dict_with_references_for_isheet(references, isheet,
                                           orientation='sources'):
    references_isheet = {}
    fieldnames = _get_fields(isheet)
    for source, isheet, field, target in references:
        if field in fieldnames:
            # FIXME we return a list of resource here, but for big data a set
            # or generator would be much better
            resources = references_isheet.get(field, [])
            if orientation == 'sources':
                resources.append(source)
            else:
                resources.append(target)
            references_isheet[field] = resources
    return references_isheet


def _get_fields(isheet):
    metadata = get_all_taggedvalues(isheet)
    fields = []
    for key, value in metadata.items():
        if key.startswith('field:'):
            name = key.split(':')[1]
            fields.append(name)
    return fields


def is_in_subtree(descendant, ancestors):
    """Check whether a resource is in a subtree below other resources.

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


def _is_candidate_ancestor(candidate, descendant, checked_candidates):
    """Return True if candidate is ancestor of descendant, False otherwise."""
    if candidate is descendant:
        return True
    checked_candidates.add(candidate.__oid__)

    children = [r[3] for r in get_references(candidate)]
    unchecked_children = [x for x in children
                          if x.__oid__ not in checked_candidates]
    for child in unchecked_children:
        if _is_candidate_ancestor(child, descendant, checked_candidates):
            return True

    return False


def get_follows(resource):
    """Determine the precessors ("follows") of a versionable resource.

    Args:
        resource (IResource)

    Returns:
        a generator of precessor versions (possibly empty)

    """
    precessors = get_references(resource, base_reftype=NewVersionToOldVersion)
    for reference in precessors:
        yield reference[3]


def get_followed_by(resource):
        """Determine the successors ("followed_by") of a versionable resource.

        Args:
            resource (IResource)

        Returns:
            a generator of successor versions (possibly empty)

        """
        successors = get_back_references(resource,
                                         base_reftype=NewVersionToOldVersion)
        for reference in successors:
            yield reference[0]
