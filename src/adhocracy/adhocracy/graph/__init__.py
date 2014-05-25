"""Utilities for working with the version/reference graph (DAG)."""

from collections import Sequence
from collections import Iterable
from collections import namedtuple

from persistent import Persistent
from substanced.util import find_objectmap
from substanced.objectmap import ObjectMap
from substanced.objectmap import Multireference

from adhocracy.interfaces import ISheet
from adhocracy.interfaces import SheetReference
from adhocracy.interfaces import SheetToSheet
from adhocracy.interfaces import NewVersionToOldVersion


_isheet_reftype = namedtuple('ISheetReftype', 'isheet field reftype')


class Reference(namedtuple('Reference', 'source isheet field target')):
    pass


class Graph(Persistent):

    """Utility to work with versions/references.

    This implementation depends on the :class:`substanced.objectmap.Objectmap`
    service.

    """

    # FIXME: add interface for graph implementations

    def __init__(self, root):
        self._root = root
        self._objectmap = find_objectmap(root)

    def get_reftypes(self, base_isheet=ISheet,
                     base_reftype=SheetReference) -> [_isheet_reftype]:
        """Collect all used SheetReferenceTypes.

        : parm objectmap: the objectmap to consult, None value is allowed to
                           ease unit testing.
        : param base_reftype: Skip types that are not subclasses of this.
        : param base_isheet: Skip types with a source isheet that is not a
                             subclass of this.
        """
        if not self._objectmap:
            return []
        all_reftypes = self._objectmap.get_reftypes()
        for reftype in all_reftypes:
            if isinstance(reftype, str):
                continue
            if not issubclass(reftype, SheetReference):
                continue
            if not reftype.isOrExtends(base_reftype):
                continue
            isheet = reftype.queryTaggedValue('source_isheet')
            if not isheet.isOrExtends(base_isheet):
                continue
            field = reftype.queryTaggedValue('source_isheet_field')
            yield _isheet_reftype(isheet, field, reftype)

    def set_references(self, source, targets: Iterable,
                       reftype: SheetReference):
        """Set references of this source.

        : param targets: the reference targets, for Sequences the order
                         is preserved.
        : param reftype: the reftype mapping to one isheet field.
        """
        assert reftype.isOrExtends(SheetReference)
        ordered = isinstance(targets, Sequence)
        orientation = 'source'
        resolve = True  # return objects not oids
        ignore_missing = True  # don't raise ValueError if targets are missing
        om = self._objectmap
        multireference = Multireference(source, om, reftype, ignore_missing,
                                        resolve, orientation, ordered)
        multireference.clear()
        multireference.connect(targets)

    def get_references(self, source, base_isheet=ISheet,
                       base_reftype=SheetToSheet) -> [Reference]:
        """Get generator with :class:`References`s of this source."""
        for isheet, field, reftype in self.get_reftypes(base_isheet,
                                                        base_reftype):
            for target in ObjectMap.targets(self._objectmap, source, reftype):
                yield Reference(source, isheet, field, target)

    def get_back_references(self, target, base_isheet=ISheet,
                            base_reftype=SheetToSheet) -> [Reference]:
        """Get generator with :class:`Reference`s with this target."""
        for isheet, field, reftype in self.get_reftypes(base_isheet,
                                                        base_reftype):
            for source in ObjectMap.sources(self._objectmap, target, reftype):
                yield Reference(source, isheet, field, target)

    def get_references_for_isheet(self, source, isheet: ISheet) -> dict:
        """ Get references of this source for one isheet only.

        : return: dictionary with the following content:
                  key - isheet field name
                  value - reference targets

                  References from subtypes of isheet are also listed.
                  Fields without existing references are ignored.
        """
        references = self.get_references(source, base_isheet=isheet)
        return self._make_references_for_isheet(references,
                                                orientation='targets')

    def get_back_references_for_isheet(self, target, isheet: ISheet) -> dict:
        """ Get references that point to this target for one isheet only.

        : return: dictionary with the following content:
                  key - isheet field name
                  value - references sources

                  References from subtypes of isheet are also listed.
                  Fields without existing references are ignored.

        """
        references = self.get_back_references(target, base_isheet=isheet)
        return self._make_references_for_isheet(references,
                                                orientation='sources')

    def _make_references_for_isheet(self, references: [Reference],
                                    orientation='sources') -> dict:
        references_isheet = {}
        for source, isheet, field, target in references:
            # FIXME we return a list of resources here, but for big data a
            # generator would be much better
            resources = references_isheet.get(field, [])
            if orientation == 'sources':
                resources.append(source)
            else:
                resources.append(target)
            references_isheet[field] = resources
        return references_isheet

    def is_in_subtree(self, descendant, ancestors: Iterable) -> bool:
        """Check whether a resource is in a subtree below other resources.

        : param descendant: the candidate descendant
        : param ancestors: the candidate ancestors
        : returns: True if there exists a relation from one of the `ancestors`
            to `descendant` that does NOT include any 'follows' links.
            For example, descendant might be an element of an element
            (of an element...) of an ancestor.
            Also if descendant and of the ancestors are the same node.

            False otherwise.

        """
        for candidate in ancestors:
            if self._is_candidate_ancestor(candidate, descendant, set(),):
                return True
        return False

    def _is_candidate_ancestor(self, candidate, descendant,
                               checked_candidates: {int}) -> bool:
        """Return True if candidate is ancestor of descendant."""
        if candidate is descendant:
            return True
        checked_candidates.add(candidate.__oid__)

        children = [r[3] for r in self.get_references(candidate)]
        unchecked_children = [x for x in children
                              if x.__oid__ not in checked_candidates]
        for child in unchecked_children:
            if self._is_candidate_ancestor(child, descendant,
                                           checked_candidates):
                return True

        return False

    def get_follows(self, resource) -> Iterable:
        """Get Generator of the precessors of a versionable resource."""
        precessors = self.get_references(resource,
                                         base_reftype=NewVersionToOldVersion)
        for reference in precessors:
            yield reference[3]

    def get_followed_by(self, resource) -> Iterable:
        """Get Generator of the successors of a versionable resource."""
        successors = self.get_back_references(
            resource,
            base_reftype=NewVersionToOldVersion)
        for reference in successors:
            yield reference[0]


def includeme(config):  # pragma: no cover
    """Graph package configuration."""
    config.include('.evolve')
