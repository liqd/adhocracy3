"""Log which user modifies resources in additional 'audit' database."""
import transaction
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

AuditEntry = namedtuple('AuditEntry', ['name',
                                       'resource_path',
                                       'user_name',
                                       'user_path'])

RESOURCE_CREATED = 'created'
RESOURCE_MODIFIED = 'modified'


class AuditLog(OOBTree):

    """An Auditlog composed of audit entries."""

    def add(self,
            name: str,
            resource_path: str,
            user_name: str,
            user_path: str) -> None:
        """ Add an audit entry to the audit log."""
        self[datetime.utcnow()] = AuditEntry(name,
                                             resource_path,
                                             user_name,
                                             user_path)


def get_auditlog(context):
    """Return the auditlog."""
    return substanced.util.get_auditlog(context)


def set_auditlog(context):
    """Set an auditlog for the context."""
    conn = context._p_jar
    try:
        auditconn = conn.get_connection('audit')
    except KeyError:
        return
    root = auditconn.root()
    if 'auditlog' in root:
        return
    auditlog = AuditLog()
    root['auditlog'] = auditlog


def log_auditevent(context, name, resource_path, user_name, user_path):
    """Add an audit entry to the audit database.

    The audit database is created if missing. If the zodbconn.uri.audit
    value is not specified in the config, auditing does not happen.
    """
    auditlog = get_auditlog(context)
    if auditlog is not None:
        auditlog.add(name, resource_path, user_name, user_path)


def audit_resources_changes_callback(request, response):
    """Add audit entries to the auditlog when the resources are changed."""
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
