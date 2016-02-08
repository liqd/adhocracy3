"""Reindex subscribers.

Read :mod:`substanced.catalog.subscribers` for default reindex subscribers.
"""

from substanced.util import find_service
from adhocracy_core.interfaces import IResourceSheetModified
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.sheets.versions import IVersionable


def reindex_decision_date(event):
    """Reindex the decision_date index for item and its versions."""
    catalogs = find_service(event.object, 'catalogs')
    catalogs.reindex_index(event.object, 'decision_date')
    children = event.object.values()
    versionables = (c for c in children if IVersionable.providedBy(c))
    for versionable in versionables:
        catalogs.reindex_index(versionable, 'decision_date')


def includeme(config):
    """Register index subscribers."""
    config.add_subscriber(reindex_decision_date,
                          IResourceSheetModified,
                          event_isheet=IWorkflowAssignment)
