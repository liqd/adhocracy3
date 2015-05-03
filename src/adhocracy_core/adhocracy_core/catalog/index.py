"""Custom catalog index."""
from hypatia.interfaces import IIndex
from hypatia.util import BaseIndexMixin
from persistent import Persistent
from substanced.catalog.indexes import SDIndex
from substanced.content import content
from substanced.util import find_objectmap
from zope.interface import implementer
import BTrees
import hypatia.query

from adhocracy_core.utils import find_graph
from adhocracy_core.interfaces import Reference


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

    def document_repr(self, docid: int, default=None) -> str:
        """Read interface."""
        objectmap = find_objectmap(self.__parent__)
        path = objectmap.path_for(docid)
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
        graph = find_graph(self.__parent__)
        return graph._objectmap.referencemap.refmap.items()

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

    def _search(self, reference: Reference) -> BTrees.LFBTree.TreeSet:
        graph = find_graph(self)
        source, isheet, isheet_field, target = reference
        if source is None and target is None:
            raise ValueError('You have to add a source or target resource')
        elif source is not None and target is not None:
            raise ValueError('Either source or target has to be None')
        if source is None:
            doc_ids = graph.get_source_ids(target, isheet, isheet_field)
        else:
            doc_ids = graph.get_target_ids(source, isheet, isheet_field)
        result = self.family.IF.TreeSet(doc_ids)
        return result
