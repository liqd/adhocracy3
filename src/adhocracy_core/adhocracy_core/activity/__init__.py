"""Create activity streams."""
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import TranslationString
from pyramid.i18n import get_localizer
from pyramid.httpexceptions import HTTPError
from pyramid.registry import Registry
from pyramid.traversal import find_interface
from pyramid.request import Request
from pyramid.response import Response
from substanced.util import find_service
from logging import getLogger
from adhocracy_core.auditing import add_to_auditlog
from adhocracy_core.events import ActivitiesGenerated
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.tags import ITags
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.utils import now
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ChangelogMetadata
from adhocracy_core.interfaces import VisibilityChange
from adhocracy_core.interfaces import ActivityType
from adhocracy_core.interfaces import Activity
from adhocracy_core.resources.comment import IComment
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.utils import get_iresource

logger = getLogger(__name__)


_ = TranslationStringFactory('adhocracy')


def update_activity_callback(request: Request, response: Response) -> None:
    """Generate activities caused by current `request` and add to the auditlog.

    This is a response-callback that runs after a request has finished.
    """
    if isinstance(response, HTTPError):
        return
    changes = _filter_trival_changes(request)
    if changes:
        activities = _create_activities(changes, request)
        activities = _add_name_to_activities(activities, request)
        event = ActivitiesGenerated(activities, request)
        request.registry.notify(event)
        add_to_auditlog(activities, request)


def _filter_trival_changes(request: Request) -> []:
    changes = request.registry.changelog.values()
    return [x for x in changes if
            _is_activity(x)
            and not x.autoupdated
            and not _is_first_version(x, request.registry)
            ]


def _is_activity(change: ChangelogMetadata) -> bool:
    data_changed = change.created or change.modified
    visibility_changed = change.visibility in [VisibilityChange.concealed,
                                               VisibilityChange.revealed]
    return data_changed or visibility_changed


def _is_first_version(change: ChangelogMetadata, registry) -> bool:
    is_version = IItemVersion.providedBy(change.resource)
    if is_version:
        follows = registry.content.get_sheet_field(change.resource,
                                                   IVersionable,
                                                   'follows')
        return follows == []
    else:
        return False


def _create_activities(changes: [ChangelogMetadata],
                       request: Request) -> [Activity]:
    activities = []
    for change in changes:
        activity_type = _get_entry_name(change)
        sheets = _get_content_sheets(change, request)
        sheet_data = _get_sheet_data(sheets)
        object = _get_object(change)
        target = _get_target(object)
        activity = Activity()._replace(subject=request.user,
                                       type=activity_type,
                                       object=object,
                                       sheet_data=sheet_data,
                                       target=target,
                                       published=now(),
                                       )
        activities.append(activity)
    return activities


def _get_entry_name(change: ChangelogMetadata) -> str:
    if change.created:
        if IItemVersion.providedBy(change.resource):
            return ActivityType.update
        else:
            return ActivityType.add
    elif change.visibility == VisibilityChange.concealed:
        return ActivityType.remove
    elif change.modified:
        if _is_workflow_state_change(change):
            return ActivityType.transition
        else:
            return ActivityType.update
    else:  # pragma: no cover
        raise ValueError('Invalid change state', change)


def _is_workflow_state_change(change: ChangelogMetadata) -> bool:
    appstructs = change.modified_appstructs or dict()
    assignment_change = [x for x in appstructs.keys()] == [IWorkflowAssignment]
    state_change = appstructs.get(IWorkflowAssignment,
                                  {}).get('workflow_state')
    return assignment_change and state_change


def _get_content_sheets(change: ChangelogMetadata, request: Request) -> []:
    if change.last_version:
        resource = change.last_version
    else:
        resource = change.resource
    content = request.registry.content
    if change.created:
        sheets = content.get_sheets_create(resource, request=request)
    elif change.modified:
        appstructs = change.modified_appstructs or dict()
        sheets = [content.get_sheet(resource, s, request=request)
                  for s in appstructs]
    else:
        sheets = content.get_sheets_edit(resource, request=request)
    disabled = [IMetadata]
    return [s for s in sheets if s.meta.isheet not in disabled]


def _get_sheet_data(sheets: [ISheet]) -> []:
    sheet_data = []
    for sheet in sheets:
            sheet_data.append({sheet.meta.isheet:
                               sheet.serialize(add_back_references=False)})
    return sheet_data


def _get_target(object: IResource) -> IResource:
    if IComment.providedBy(object):
        # assuming all comments from one service are commenting a
        # single process content
        comments_service = find_service(object, 'comments')
        commented_content = comments_service and comments_service.__parent__
        return commented_content
    else:
        return object.__parent__


def _get_object(change: ChangelogMetadata) -> IResource:
    if IItemVersion.providedBy(change.resource):
        item = find_interface(change.resource, IItem)
        return item
    else:
        return change.resource


def _add_name_to_activities(activities: [Activity],
                            request: Request) -> [Activity]:
    activities_with_name = []
    for activity in activities:
        name = generate_activity_name(activity, request)
        activities_with_name.append(activity._replace(name=name))
    return activities_with_name


def generate_activity_name(activity: Activity,
                           request: Request) -> TranslationString:
    """Create name for activity and return translation string.

    The following variables are provided for the translation string:

        - `subject_name`
        - `object_type_name`
        - `target_title`
    """
    registry = request.registry
    mapping = {'subject_name': _get_subject_name(activity.subject, registry),
               'object_type_name': _get_type_name(activity.object, request),
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
    elif activity.type == ActivityType.transition:
        name = _('activity_name_transition',
                 mapping=mapping,
                 default=u'${subject_name} changed workflow state of '
                         '${object_type_name}.')
    else:
        name = _('activity_missing', mapping=mapping)
    return name


def generate_activity_description(activity: Activity,
                                  request: Request) -> TranslationString:
    """Create description for activity and return translation string.

    The following variables are provided for the translation string:

        - `subject_name`
        - `object_type_name`
        - `object_title`
        - `target_type_name`
        - `target_title`
    """
    registry = request.registry
    mapping = {'subject_name': _get_subject_name(activity.subject, registry),
               'object_title': _get_title(activity.object, registry),
               'object_type_name': _get_type_name(activity.object, request),
               'target_title': _get_title(activity.target, registry),
               'target_type_name': _get_type_name(activity.target, request),
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
    elif activity.type == ActivityType.transition:
        name = _('activity_description_transition',
                 mapping=mapping,
                 default=u'${subject_name} changed workfow state of '
                         '"${object_title}".')
    else:
        name = _('activity_missing', mapping=mapping)
    return name


def _get_subject_name(user: IUserBasic, registry: Registry) -> str:
    if user is None:
        name = 'Application'
    else:
        name = registry.content.get_sheet_field(user, IUserBasic, 'name')
    return name


def _get_type_name(context: IResource, request: Request) -> str:
    localizer = get_localizer(request)
    if context is None:
        translated_name = ''
    else:
        iresource = get_iresource(context)
        name = request.registry.content.resources_meta[iresource].content_name
        translated_name = localizer.translate(name)
    return translated_name


def _get_title(context: IResource, registry: Registry) -> str:
    from adhocracy_core.sheets.comment import IComment
    if IItem.providedBy(context):
        context = registry.content.get_sheet_field(context, ITags, 'LAST')
    if ITitle.providedBy(context):
        name = registry.content.get_sheet_field(context, ITitle, 'title')
    elif IComment.providedBy(context):
        name = registry.content.get_sheet_field(context, IComment, 'content')
    else:
        name = ''
    return name
