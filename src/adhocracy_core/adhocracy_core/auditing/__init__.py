"""Log which user modifies resources in additional 'audit' database."""
import transaction
import substanced.util

from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import TranslationString
from pyramid.registry import Registry
from pyramid.traversal import find_interface
from pyramid.traversal import resource_path
from pyramid.request import Request
from pyramid.response import Response
from BTrees.OOBTree import OOBTree
from logging import getLogger
from adhocracy_core.events import ActivitiesAddedToAuditLog
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.utils import now
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.interfaces import SerializedActivity
from adhocracy_core.interfaces import ActivityType
from adhocracy_core.interfaces import Activity
from adhocracy_core.utils import get_iresource

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


def update_auditlog_callback(request: Request, response: Response) -> None:
    """Add activities caused by current `request` to the auditlog.

    This is a response-callback that runs after a request has finished. To
    store the audit entry it adds an additional transaction.
    """
    changelog = request.registry.changelog
    changes = _filter_trival_changes(changelog.values())
    activities = _create_activities(changes, request)
    activities = _add_name_to_activities(activities, request.registry)
    add_to_auditlog(activities, request)
    transaction.commit()


def _filter_trival_changes(changes: [ChangelogMetadata]) -> []:
    return [x for x in changes if _is_activity(x) and
            not x.autoupdated]


def _create_activities(changes: [ChangelogMetadata],
                       request: Request) -> [Activity]:
    activities = []
    for change in changes:
        activity_type = _get_entry_name(change)
        sheets = _get_content_sheets(change, request.registry)
        sheet_data = _get_sheet_data(sheets, request)
        target = _get_target(change)
        activity = Activity()._replace(subject=request.user,
                                       type=activity_type,
                                       object=change.resource,
                                       sheet_data=sheet_data,
                                       target=target,
                                       published=now(),
                                       )
        activities.append(activity)
    return activities


def _is_activity(change: ChangelogMetadata) -> bool:
    data_changed = change.created or change.modified
    visibility_changed = change.visibility in [VisibilityChange.concealed,
                                               VisibilityChange.revealed]
    return data_changed or visibility_changed


def _get_entry_name(change: ChangelogMetadata) -> str:
    if change.created:
        if IItemVersion.providedBy(change.resource):
            return ActivityType.update
        else:
            return ActivityType.add
    elif change.modified:
        return ActivityType.update
    elif change.visibility == VisibilityChange.concealed:
        return ActivityType.remove
    else:
        raise ValueError('Invalid change state', change)


def _get_content_sheets(change: ChangelogMetadata, registry: Registry) -> []:
    if change.created:
        sheets = registry.content.get_sheets_create(change.resource)
    else:
        sheets = registry.content.get_sheets_edit(change.resource)
    return sheets


def _get_sheet_data(sheets: [ISheet], request: Request) -> {}:
    sheet_data = []
    _disabled = [IMetadata]
    for sheet in sheets:
        if sheet.meta.isheet not in _disabled:
            sheet.request = request
            sheet_data.append({sheet.meta.isheet:
                               sheet.serialize(add_back_references=False)})
    return sheet_data


def _get_target(change: ChangelogMetadata) -> IResource:
        if IItemVersion.providedBy(change.resource):
            item = find_interface(change.resource, IItem)
            return item
        else:
            return change.resource.__parent__


def _add_name_to_activities(activities: [Activity],
                            registry: Registry) -> [Activity]:
    activities_with_name = []
    for activity in activities:
        name = generate_activity_name(activity, registry)
        activities_with_name.append(activity._replace(name=name))
    return activities_with_name


def generate_activity_name(activity: Activity,
                           registry: Registry) -> TranslationString:
    """Create name for activity and return translation string.

    The following variables are provided for the translation string:

        - `subject_name`
        - `object_type_name`
        - `target_title`
    """
    mapping = {'subject_name': _get_subject_name(activity.subject, registry),
               'object_type_name': _get_type_name(activity.object, registry),
               'target_title': _get_title(activity.target, registry),
               }
    if activity.type == ActivityType.add:
        name = _('activity_name_add',
                 mapping=mapping,
                 default=u'${subject_name} added a ${object_type_name} to '
                         '${target_title}.')
    elif activity.type == ActivityType.update:
        name = _('activity_name_update',
                 mapping=mapping,
                 default=u'${subject_name} updated ${object_type_name}')
    elif activity.type == ActivityType.remove:
        name = _('activity_name_remove',
                 mapping=mapping,
                 default=u'${subject_name} removed a ${object_type_name} from '
                         '${target_title}.')
    else:
        name = _('activity_missing', mapping=mapping)
    return name


def generate_activity_description(activity: Activity,
                                  registry: Registry) -> TranslationString:
    """Create description for activity and return translation string.

    The following variables are provided for the translation string:

        - `subject_name`
        - `object_type_name`
        - `object_title`
        - `target_type_name`
        - `target_title`
    """
    mapping = {'subject_name': _get_subject_name(activity.subject, registry),
               'object_title': _get_title(activity.target, registry),
               'object_type_name': _get_type_name(activity.object, registry),
               'target_title': _get_title(activity.target, registry),
               'target_type_name': _get_type_name(activity.target, registry),
               }
    if activity.type == ActivityType.add:
        name = _('activity_description_add',
                 mapping=mapping,
                 default=u'${subject_name} added the ${object_type_name} '
                         '"${object_title}" to ${target_type_name} '
                         '"${target_title}".')
    elif activity.type == ActivityType.update:
        name = _('activity_description_update',
                 mapping=mapping,
                 default=u'${subject_name} updated ${object_type_name} '
                         '"${object_title}".')
    elif activity.type == ActivityType.remove:
        name = _('activity_description_remove',
                 mapping=mapping,
                 default=u'${subject_name} removed the ${object_type_name} '
                         '"${object_title}" from ${target_type_name} '
                         '"${target_title}".')
    else:
        name = _('activity_missing', mapping=mapping)
    return name


def _get_subject_name(user: IUserBasic, registry: Registry) -> str:
    if user is None:
        name = 'Application'
    else:
        name = registry.content.get_sheet_field(user, IUserBasic, 'name')
    return name


def _get_type_name(context: IResource, registry: Registry) -> str:
    if context is None:
        name = ''
    else:
        iresource = get_iresource(context)
        name = registry.content.resources_meta[iresource].content_name
    return name


def _get_title(context: IResource, registry: Registry) -> str:
    from adhocracy_core.sheets.title import ITitle
    if ITitle.providedBy(context):
        name = registry.content.get_sheet_field(context, ITitle, 'title')
    else:
        name = ''
    return name
