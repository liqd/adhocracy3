"""Utilities for working with the version/reference graph (DAG)."""

from collections import namedtuple
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Sequence

from persistent import Persistent
from pyramid.registry import Registry

from substanced.util import find_objectmap
from substanced.objectmap import ObjectMap
from substanced.objectmap import Multireference
from substanced.content import content
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import Reference
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetReference
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.events import SheetBackReferenceRemoved
from adhocracy_core.events import SheetBackReferenceAdded


class SheetReftype(namedtuple('ISheetReftype', 'isheet field reftype')):

    """Fields: isheet field reftype."""


@content('Graph',
         )
class Graph(Persistent):

    """Utility to work with versions/references.

    This implementation depends on the :class:`substanced.objectmap.Objectmap`
    service.

    """

    # FIXME: add interface for graph implementations
    def __init__(self, context):
        self.context = context

    @property
    def _objectmap(self):
        return find_objectmap(self.context)

    def get_reftypes(self, base_isheet=ISheet,
                     base_reftype=SheetReference) -> Iterator:
        """Collect all used SheetReferenceTypes.

        :param base_reftype: Skip types that are not subclasses of this.
        :param base_isheet: Skip types with a source isheet that is not a
                            subclass of this.
        :returns: Generator of :class:`adhocracy_core.graph.SheetReftype`
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
            yield SheetReftype(isheet, field, reftype)

    def set_references(self, source, targets: Iterable,
                       reftype: SheetReference, registry: Registry=None):
        """Set references of this source.

        :param targets: the reference targets, for Sequences the order
                         is preserved.
        :param reftype: the reftype mapping to one isheet field.
        :param registry: pyramid registry to notify referenced resources.
                         Default value is None to ease testing.
        """
        assert reftype.isOrExtends(SheetReference)
        multireference = self._create_multireference(source, targets, reftype)
        old = set([x for x in multireference])
        multireference.clear()
        multireference.connect(targets)
        if registry is None:
            return
        new = set(targets)
        removed = old - new
        self._notify_removed_targets(source, reftype, removed, registry)
        added = new - old
        self._notify_added_targets(source, reftype, added, registry)

    def _create_multireference(self, source, targets, reftype):
        ordered = isinstance(targets, Sequence)
        orientation = 'source'
        resolve = True  # return objects not oids
        ignore_missing = True  # don't raise ValueError if targets are missing
        om = self._objectmap
        multireference = Multireference(source, om, reftype, ignore_missing,
                                        resolve, orientation, ordered)
        return multireference

    def _notify_removed_targets(self, source, reftype, targets, registry):
        reference_tmpl = self._create_reference_template(source, reftype)
        target_isheet = reftype.queryTaggedValue('target_isheet')
        for target in targets:
            reference = reference_tmpl._replace(target=target)
            event = SheetBackReferenceRemoved(target, target_isheet, reference,
                                              registry)
            registry.notify(event)

    def _notify_added_targets(self, source, reftype, targets, registry):
        reference_tmpl = self._create_reference_template(source, reftype)
        target_isheet = reftype.queryTaggedValue('target_isheet')
        for target in targets:
            reference = reference_tmpl._replace(target=target)
            event = SheetBackReferenceAdded(target, target_isheet, reference,
                                            registry)
            registry.notify(event)

    def _create_reference_template(self, source, reftype):
        source_isheet = reftype.queryTaggedValue('source_isheet')
        source_isheet_field = reftype.queryTaggedValue('target_isheet_field')
        return Reference(source, source_isheet, source_isheet_field, None)

    def get_references(self, source, base_isheet=ISheet,
                       base_reftype=SheetReference) -> Iterator:
        """Get generator of :class:`Reference` with this `source`."""
        for isheet, field, reftype in self.get_reftypes(base_isheet,
                                                        base_reftype):
            for target in ObjectMap.targets(self._objectmap, source, reftype):
                yield Reference(source, isheet, field, target)

    def get_back_references(self, target, base_isheet=ISheet,
                            base_reftype=SheetReference) -> Iterator:
        """Get generator of :class:`Reference` with this `target`."""
        for isheet, field, reftype in self.get_reftypes(base_isheet,
                                                        base_reftype):
            for source in ObjectMap.sources(self._objectmap, target, reftype):
                yield Reference(source, isheet, field, target)

    def get_back_reference_sources(self,
                                   resource,
                                   reftype=SheetReference) -> Iterable:
        """Get generator of the sources of backreferences.

        :param resource: the resource whose backreferences we want
        :param reftype: the type of backreferences we want
        :return: a generator of reference sources (sheets referring to the
                 resource)
        """
        comment_refs = self.get_back_references(resource, base_reftype=reftype)
        for reference in comment_refs:
            yield reference.source

    def set_references_for_isheet(self, source, isheet: ISheet,
                                  references: dict, registry: Registry):
        """ Set references of this source for one isheet.

        :param references: dictionary with the following content:
                           key - isheet field name
                           value - reference targets
        :param registry: Pyramid Registry with
                         :class:`adhocracy_core.registry.ResourceContentRegistry`
                         attribute named `content`.
        """
        sheet_meta = registry.content.sheets_meta[isheet]
        schema = sheet_meta.schema_class()
        for field_name, targets in references.items():
            assert field_name in schema
            if targets is None:
                continue
            node = schema[field_name]
            reftype = getattr(node, 'reftype', None)
            if reftype is None:
                continue
            if IResource.providedBy(targets):
                targets = [targets]
            self.set_references(source, targets, reftype, registry)

    def get_references_for_isheet(self, source, isheet: ISheet) -> dict:
        """ Get references of this source for one isheet only.

        :returns: dictionary with the following content:
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

    def _make_references_for_isheet(self, references: Iterable,
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

        :param descendant: the candidate descendant
        :param ancestors: the candidate ancestors
        :returns: True if there exists a relation from one of the `ancestors`
            to `descendant` that does NOT include any 'follows' links.
            For example, descendant might be an element of an element
            (of an element...) of an ancestor.
            Also if descendant and one of the ancestors are the same node.

            False otherwise.

        """
        for candidate in ancestors:
            if self._is_candidate_ancestor(candidate, descendant, set(),):
                return True
        return False

    def _is_candidate_ancestor(self, candidate, descendant,
                               checked_candidates: set) -> bool:
        """Return True if candidate is ancestor of descendant."""
        if candidate is descendant:
            return True
        checked_candidates.add(candidate.__oid__)
        references = self.get_references(candidate, base_reftype=SheetToSheet)
        children = [ref.target for ref in references]
        unchecked_children = [x for x in children
                              if x.__oid__ not in checked_candidates]
        for child in unchecked_children:
            if self._is_candidate_ancestor(child, descendant,
                                           checked_candidates):
                return True

        return False


def includeme(config):  # pragma: no cover
    """Register Graph content type."""
    config.scan('.', ignore='.test_init')
