"""Log which user modifies resources in additional 'audit' database."""
import transaction
import substanced.util

from pyramid.traversal import resource_path
from pyramid.request import Request
from pyramid.response import Response
from BTrees.OOBTree import OOBTree
from datetime import datetime
from logging import getLogger
from collections import namedtuple
from enum import Enum
from adhocracy_core.utils import get_user
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.utils import get_sheet_field
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange

logger = getLogger(__name__)

AuditEntry = namedtuple('AuditEntry', ['name',
                                       'resource_path',
                                       'user_name',
                                       'user_path'])


class EntryName(Enum):
    created = 'created'
    modified = 'modified'
    # visible = 'visible' is not necessary since
    # VisibilityChange.visible is only a state, not a change
    invisible = 'invisible'
    concealed = 'concealed'
    revealed = 'revealed'


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


def get_auditlog(context: IResource) -> AuditLog:
    """Return the auditlog."""
    return substanced.util.get_auditlog(context)


def set_auditlog(context: IResource) -> None:
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


def log_auditevent(context: IResource,
                   name: str,
                   resource_path: str,
                   user_name: str,
                   user_path: str) -> None:
    """Add an audit entry to the audit database.

    The audit database is created if missing. If the zodbconn.uri.audit
    value is not specified in the config, auditing does not happen.
    """
    auditlog = get_auditlog(context)
    if auditlog is not None:
        auditlog.add(name, resource_path, user_name, user_path)


def audit_resources_changes_callback(request: Request,
                                     response: Response) -> None:
    """Add audit entries to the auditlog when the resources are changed."""
    registry = request.registry
    changelog_metadata = registry.changelog.values()
    user_name, user_path = _get_user_info(request)
    for meta in changelog_metadata:
        _log_change(request.context, user_name, user_path, meta)


def _get_user_info(request: Request) -> (str, str):
    if not hasattr(request, 'authenticated_userid'):
        # request has no associated user
        return ('', '')
    user = get_user(request)
    if user is None:
        return ('', '')
    else:
        user_name = get_sheet_field(user, IUserBasic, 'name')
        user_path = resource_path(user)
        return (user_name, user_path)


def _log_change(context: IResource,
                user_name: str,
                user_path: str,
                change: ChangelogMetadata) -> None:
    if change.created or change.modified or \
       change.visibility is not None and \
       change.visibility is not VisibilityChange.visible:
        log_auditevent(context,
                       _get_entry_name(change),
                       resource_path=resource_path(change.resource),
                       user_name=user_name,
                       user_path=user_path)
        transaction.commit()


def _get_entry_name(change) -> str:
    if change.created:
        return EntryName.created
    elif change.modified:
        return EntryName.modified
    elif change.visibility == VisibilityChange.invisible:
        return EntryName.invisible
    elif change.visibility == VisibilityChange.concealed:
        return EntryName.concealed
    elif change.visibility == VisibilityChange.revealed:
        return EntryName.revealed
    else:
        raise ValueError('Invalid change state', change)
