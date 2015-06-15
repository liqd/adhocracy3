"""Custom catalog index."""
from hypatia.interfaces import IIndex
from hypatia.util import BaseIndexMixin
from hypatia.util import ResultSet
from persistent import Persistent
from pyramid.decorator import reify
from substanced.catalog.indexes import SDIndex
from substanced.content import content
from substanced.util import find_objectmap
from zope.interface import implementer
import BTrees
import hypatia.query

from adhocracy_core.utils import find_graph
from adhocracy_core.interfaces import Reference
from adhocracy_core.interfaces import ISheet


@content('Reference Index',
         is_index=True,
         )
@implementer(IIndex)
class ReferenceIndex(SDIndex, BaseIndexMixin, Persistent):

    """Use :func:`adhocracy_core.graph.Graph.get_source_ids` to query refs."""

    family = BTrees.family64
    __parent__ = None
    __name__ = None

    def __init__(self, discriminator=None):
        self._not_indexed = self.family.IF.TreeSet()

    @reify
    def _graph(self):
        return find_graph(self)

    @reify
    def _objectmap(self):
        return find_objectmap(self)

    def document_repr(self, docid: int, default=None) -> str:
        """Read interface."""
        path = self._objectmap.path_for(docid)
        if path is None:
            return default
        return path

    def reset(self):
        """Read interface."""
        self._not_indexed.clear()

    def index_doc(self, docid: int, context):
        """Read interface."""
        pass

    def unindex_doc(self, docid):
        """Read interface."""
        pass

    def reindex_doc(self, docid, obj):
        """Read interface."""
        pass

    def docids(self):
        """Read interface."""
        return self._objectmap.referencemap.refmap.items()

    indexed = docids
    """Read docids docstring."""

    def not_indexed(self):
        """Read interface."""
        return self._not_indexed

    def eq(self, reference: Reference) -> hypatia.query.Eq:
        """Eq operator to concatenate queries.."""
        query = {'reference': reference}
        return hypatia.query.Eq(self, query)

    def apply(self, query: dict) -> BTrees.family64.IF.TreeSet:
        """Apply query parameters·{reference: Reference} and return result."""
        reference = query['reference']
        return self._search(reference)

    applyEq = apply
    """Read apply docsting."""

    def search_with_order(self, reference: Reference) -> ResultSet:
        """"Search target or source resources ids of `reference` with order."""
        oids = [x for x in self._search_target_or_source_ids(reference)]
        result = ResultSet(oids, len(oids), None)
        return result

    def _search(self, reference: Reference) -> BTrees.LFBTree.TreeSet:
        """"Search target or soruce resources of `reference` without order.

        This helper function is to fullfill the IIndex interface.
        """
        oids = self._search_target_or_source_ids(reference)
        result = self.family.IF.TreeSet(oids)
        return result

    def _search_target_or_source_ids(self, reference) -> [int]:
        source, isheet, isheet_field, target = reference
        if source is None and target is None:
            raise ValueError('You have to add a source or target resource')
        elif source is not None and target is not None:
            raise ValueError('Either source or target has to be None')
        if source is None:
            oids = self._resource_ids(target, isheet, isheet_field, 'sources')
        else:
            oids = self._resource_ids(source, isheet, isheet_field, 'targets')
        return oids

    def _resource_ids(self, resource, isheet=ISheet, isheet_field='',
                      orientation='') -> set:
        """Get OIDs from references with `orientation` targets or sources."""
        if orientation == 'sources':
            get_resources_ids = self._objectmap.sourceids
        else:
            get_resources_ids = self._objectmap.targetids
        for isheet, field, reftype in self._graph.get_reftypes(isheet):
            if isheet_field and field != isheet_field:
                continue
            for oid in get_resources_ids(resource, reftype):
                yield oid
