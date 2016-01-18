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
        """Initialize self."""
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

    def eq(self, query: dict) -> hypatia.query.Eq:
        """Concatenate reference `query`.

        :param query:

            reference (Reference): reference with target or source
            traverse (bool): traverse all references with same type, starting
                             with the given target or source.
        """
        return hypatia.query.Eq(self, query)

    def apply(self, query: dict) -> BTrees.family64.IF.TreeSet:
        """Apply reference `query`.

        :param query:

            reference (Reference): reference with target or source
            traverse (bool): traverse all references with same type, starting
                             with the given target or source.
        """
        if 'traverse' not in query:
            query['traverse'] = False
        return self._search(query)

    def applyAll(self, queries: [dict]) -> BTrees.family64.IF.TreeSet:  # noqa
        """Apply multiple reference `queries`.

        The result sets are combined with `intersection`.
        """
        result_all = set(self._search(queries[0]))
        for reference in queries[1:]:
            result = set(self._search(reference))
            result_all = result_all.intersection(result)
        return result_all

    applyEq = apply
    """Read apply docsting."""

    def search_with_order(self, reference: Reference) -> ResultSet:
        """"Search target or source resources ids of `reference` with order."""
        query = {'reference': reference,
                 'traverse': False}
        oids = [x for x in self._search_target_or_source_ids(query)]
        result = ResultSet(oids, len(oids), None)
        return result

    def _search(self, query: dict) -> BTrees.LFBTree.TreeSet:
        """"Search target or source resources of `reference` without order."""
        oids = self._search_target_or_source_ids(query)
        result = self.family.IF.TreeSet(oids)
        return result

    def _search_target_or_source_ids(self, query: dict) -> [int]:
        source, isheet, isheet_field, target = query['reference']
        if source is None and target is None:
            raise ValueError('You have to add a source or target resource')
        elif source is not None and target is not None:
            raise ValueError('Either source or target has to be None')
        traverse = query['traverse']
        if source is None:
            oids = self._resource_ids(target, isheet, isheet_field, 'sources',
                                      traverse=traverse)
        else:
            oids = self._resource_ids(source, isheet, isheet_field, 'targets',
                                      traverse=traverse)
        return oids

    def _resource_ids(self, resource, isheet=ISheet, isheet_field='',
                      orientation='',
                      traverse=False) -> set:
        """Get OIDs from references with `orientation` targets or sources."""
        if orientation == 'sources':
            get_resources_ids = self._objectmap.sourceids
        else:
            get_resources_ids = self._objectmap.targetids
        for isheet, field, reftype in self._graph.get_reftypes(isheet):
            if isheet_field and field != isheet_field:
                continue
            for oid in get_resources_ids(resource, reftype):
                if traverse:
                    yield from self._resource_ids(oid,
                                                  isheet=isheet,
                                                  isheet_field=isheet_field,
                                                  orientation=orientation,
                                                  traverse=traverse)
                yield oid
