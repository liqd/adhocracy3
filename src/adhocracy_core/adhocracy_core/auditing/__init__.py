"""Auditlog of events stored in a ZODB database."""
import transaction
import json
import substanced.util

from pyramid.traversal import resource_path
from BTrees.OOBTree import OOBTree
from datetime import datetime
from logging import getLogger
from collections import namedtuple
from adhocracy_core.utils import get_user
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.utils import get_sheet_field


logger = getLogger(__name__)

AuditEntry = namedtuple('AuditEntry', ['name', 'payload'])

RESOURCE_CREATED = 'resourceCreated'
RESOURCE_MODIFIED = 'resourceModified'


class AuditLog(OOBTree):

    """An Auditlog composed of entries."""

    def add(self, name, **kw):
        """ Add a record the audit log.

        ``_name`` should be the event name,
        ``_oid`` should be an object oid or ``None``, and ``kw`` should be a
        json-serializable dictionary.
        """
        payload = json.dumps(kw)
        self[datetime.utcnow()] = AuditEntry(name, payload)


def get_auditlog(context):
    """Return the auditlog. Create one if none exits."""
    auditlog = substanced.util.get_auditlog(context)
    if auditlog is None:
        _set_auditlog(context)
        transaction.commit()
        auditlog = substanced.util.get_auditlog(context)
        # auditlog can still be None after _set_auditlog if not audit
        # conn has been configured
        if auditlog is not None:
            logger.info('Auditlog created')
        return auditlog
    return auditlog


def _set_auditlog(context):
    """Set an auditlog for the context."""
    conn = context._p_jar
    try:
        auditconn = conn.get_connection('audit')
    except KeyError:
        return
    root = auditconn.root()
    if 'auditlog' not in root:
        auditlog = AuditLog()
        root['auditlog'] = auditlog


def log_auditevent(context, name, **kw):
    """Add a an audit entry to the audit database.

    The audit database is created if missing. If the zodbconn.uri.audit
    value is not specified in the config, auditing does not happen.
    """
    auditlog = get_auditlog(context)
    if auditlog is not None:
        auditlog.add(name, **kw)


def audit_changes_callback(request, response):
    """Add audit entries to the auditlog when the data is changed."""
    registry = request.registry
    changelog_metadata = registry.changelog.values()
    if len(changelog_metadata) == 0:
        return

    (user_name, user_path) = _get_user_info(request)

    for meta in changelog_metadata:
        _log_change(request.context, user_name, user_path, meta)


def _get_user_info(request):
    user = get_user(request)
    if user is None:
        return ('', '')
    else:
        user_name = get_sheet_field(user, IUserBasic, 'name')
        user_path = resource_path(user)
        return (user_name, user_path)


def _log_change(context, user_name, user_path, change):
    path = resource_path(change.resource)
    if change.created:
        log_auditevent(context,
                       RESOURCE_CREATED,
                       resource_path=path,
                       user_name=user_name,
                       user_path=user_path)
    elif change.modified:
        log_auditevent(context,
                       RESOURCE_MODIFIED,
                       resource_path=path,
                       user_name=user_name,
                       user_path=user_path)
    # else: log visibility changes?
    transaction.commit()
