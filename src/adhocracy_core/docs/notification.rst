Notification
============

Each user can enable notifications about activities. Activities are resource
modifications made by other users/groups or the application itself.
The user resource is responsible to follow activities regarding specific
resources, filter activity types and configure how the user is notified.

Preliminaries
-------------

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.process import IProcess
    >>> from adhocracy_core.resources.document import IDocument
    >>> from adhocracy_core.resources.document import IDocumentVersion
    >>> from adhocracy_core.sheets.notification import INotification
    >>> from adhocracy_core.sheets.title import ITitle
    >>> from adhocracy_core.sheets.description import IDescription

Start adhocracy app and log in some users::

    >>> app_admin = getfixture('app_admin')
    >>> app_participant = getfixture('app_participant')
    >>> participant_path = app_participant.user_path
    >>> app_participant2 = getfixture('app_participant2')

Setup some basic content::

    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'process'},
    ...         'adhocracy_core.sheets.title.ITitle': {'title': 'Process Title'},
    ...         }
    >>> resp = app_admin.post_resource('/', IProcess, data)
    >>> process_path = resp.json['path']

Following
---------

On default you don`t follow any resource:

    >>> resp = app_participant.get(participant_path).json
    >>> resp['data'][INotification.__identifier__]
    {'follow_resources': []}

Lets follow a process::

    >>> data = {'data': {INotification.__identifier__:
    ...     {'follow_resources': [process_path]}}}
    >>> resp= app_participant.put(participant_path, data)
    >>> resp.status_code
    200

Email notification
------------------

If another user adds a new process content

    >>> data = [
    ...     {'method': 'POST', 'path': process_path, 'result_path': '@par1_item','result_first_version_path': '@par1_item/v1',
    ...      'body': {'content_type': IDocument.__identifier__,
    ...               'data': {}}
    ...       },
    ...     {'method': 'POST', 'path': '@par1_item', 'result_path': '@par1_item/v2',
    ...      'body': {'content_type': IDocumentVersion.__identifier__,
    ...               'data': {'adhocracy_core.sheets.versions.IVersionable': {
    ...                         'follows': ['@par1_item/v1']
    ...                        },
    ...                       ITitle.__identifier__: {
    ...                         'title': 'Document Title'
    ...                        },
    ...               }},
    ...       },]
    >>> resp = app_participant2.batch(data)
    >>> resp.status_code
    200

a notification email is send:

    >>> mails = getfixture('mails')
    >>> send_mails = mails.send()
    >>> len(send_mails)
    2

#FIXME there should be only 1 mail, we need to filter autoupdates for this.

    >>> activity_mail = [x for x in send_mails if 'added' in x.subject][0]
    >>> activity_mail.subject
    'Adhocracy: participant2 added a Document to Process Title.'

    >>> activity_mail.body
    'participant2 added the Document "Process Title" to Process "Process Title". Visit: http://localhost:6551/r/process/document_0000000/ .'
