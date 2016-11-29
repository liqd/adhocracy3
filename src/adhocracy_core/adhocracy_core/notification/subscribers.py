"""Subscribers to send activity notifications to users."""
from collections import defaultdict
from pyramid.interfaces import IRequest
from pyramid.traversal import find_interface
from substanced.util import find_service

from adhocracy_core.interfaces import Activity
from adhocracy_core.interfaces import ActivityType
from adhocracy_core.interfaces import search_query
from adhocracy_core.interfaces import Reference
from adhocracy_core.interfaces import IActivitiesGenerated
from adhocracy_core.sheets.notification import INotification
from adhocracy_core.sheets.notification import IFollowable
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.resources.comment import IComment
from adhocracy_core.resources.process import IProcess


def send_activity_notification_emails(event: IActivitiesGenerated):
    """Notify users about activities regarding resources they follow."""
    streams = _create_resource_streams(event.activities)
    subscriptions = _get_follow_subscriptions(streams, event.request)
    _send_emails(subscriptions, streams, event.request)


def _create_resource_streams(activities: [Activity]) -> [tuple]:
    streams = defaultdict(list)
    for activity in activities:
        if activity.type == ActivityType.transition:
            continue
        if _is_workflow_assignment_update(activity):
            continue
        if IFollowable.providedBy(activity.object):
            streams[activity.object].append(activity)
        if IFollowable.providedBy(activity.target):
            streams[activity.target].append(activity)
        if IComment.providedBy(activity.object):
            process = find_interface(activity.object, IProcess)
            if process and IFollowable.providedBy(process):
                streams[process].append(activity)
    return sorted(streams.items(), key=lambda x: x[1][0].published)


def _is_workflow_assignment_update(activity: Activity) -> bool:
    for x in activity.sheet_data:
        if IWorkflowAssignment in x:
            return True
    return False


def _get_follow_subscriptions(streams: [tuple],
                              request: IRequest) -> dict:
    context = request.root
    catalogs = find_service(context, 'catalogs')
    subscriptions = defaultdict(set)
    for resource in [x for x, y in streams]:
        ref = Reference(None, INotification, 'follow_resources', resource)
        query = search_query._replace(references=(ref,))
        followers = catalogs.search(query).elements
        for follower in followers:
            subscriptions[resource].add(follower)
    return subscriptions


def _send_emails(subscriptions: dict, streams: [tuple], request: IRequest):
    messenger = request.registry.messenger
    for resource, activites in streams:
        for follower in subscriptions[resource]:
            for activity in activites:
                if activity.subject != follower:
                    messenger.send_activity_mail(follower, activity, request)


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(send_activity_notification_emails,
                          IActivitiesGenerated)
