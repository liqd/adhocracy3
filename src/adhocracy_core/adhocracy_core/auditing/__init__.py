"""Log which user modifies resources in additional 'audit' database."""
import substanced.util

from pyramid.i18n import TranslationStringFactory
from pyramid.traversal import resource_path
from pyramid.request import Request
from BTrees.OOBTree import OOBTree
from logging import getLogger
from adhocracy_core.events import ActivitiesAddedToAuditLog
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import SerializedActivity
from adhocracy_core.interfaces import Activity

logger = getLogger(__name__)


_ = TranslationStringFactory('adhocracy')


class AuditLog(OOBTree):
    """An Auditlog composed of audit entries.

    This is a dictionary (:class:`collections.abc.Mapping`) with key
    :class:`datetime.datetime` and value
    :class:`adhocracy_core.interfaces.SerializedActivity`.

    The methods `items`, `keys`, and `values` have the additional kwargs
    `max_key` and `min_key` to allow range queries::

       january = datetime(2015, 1, 1)
       february = datetime(2015, 2, 1)
       audit = get_auditlog(context)
       audit.items(min=january, max=february)
       ...

    """

    def add(self, activity: Activity) -> None:
        """Serialize `activity` and store in audit log."""
        kwargs = {'object_path': resource_path(activity.object),
                  'type': activity.type,
                  }
        if activity.subject:
            kwargs['subject_path'] = resource_path(activity.subject)
        if activity.target:
            kwargs['target_path'] = resource_path(activity.target)
        if activity.sheet_data:
            kwargs['sheet_data'] = activity.sheet_data
        entry = SerializedActivity()._replace(**kwargs)
        self[activity.published] = entry


def get_auditlog(context: IResource) -> AuditLog:
    """Return the auditlog."""
    return substanced.util.get_auditlog(context)


def set_auditlog(context: IResource) -> None:
    """Set an auditlog for the context."""
    conn = context._p_jar
    try:
        connection = conn.get_connection('audit')
    except KeyError:
        return
    root = connection.root()
    if 'auditlog' in root:
        return
    auditlog = AuditLog()
    root['auditlog'] = auditlog


def add_to_auditlog(activities: [Activity],
                    request: Request) -> None:
    """Add activities to the audit database.

    The audit database is created if missing. If the `zodbconn.uri.audit`
    value is not specified in the config, auditing does not happen.
    """
    auditlog = get_auditlog(request.root)
    event = ActivitiesAddedToAuditLog(auditlog, activities, request)
    request.registry.notify(event)
    if auditlog is None:
        return
    for activity in activities:
        auditlog.add(activity)
