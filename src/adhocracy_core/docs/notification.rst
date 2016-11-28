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
    >>> from adhocracy_core.resources.comment import IComment
    >>> from adhocracy_core.resources.comment import ICommentVersion
    >>> from adhocracy_core.sheets.notification import INotification
    >>> from adhocracy_core.sheets.title import ITitle
    >>> from adhocracy_core.sheets.description import IDescription

Start adhocracy app and log in some users::

    >>> app_admin = getfixture('app_admin')
    >>> app_participant = getfixture('app_participant')
    >>> participant_path = app_participant.user_path
    >>> app_participant2 = getfixture('app_participant2')
    >>> send_mails = getfixture('send_mails')

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
    >>> resp['data'][INotification.__identifier__].get('follow_resources')
    []

Lets follow a process::

    >>> data = {'data': {INotification.__identifier__:
    ...     {'follow_resources': [process_path]}}}
    >>> resp= app_participant.put(participant_path, data)
    >>> resp.status_code
    200

Email notification
------------------

The user ist notified by email about user activities regarding his followed resources.


Added content:

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
    >>> document_path = resp.json['responses'][0]['body']['path']
    >>> document_path_last_version = resp.json['responses'][1]['body']['path']

    >>> send_mails[-1].subject
    'Adhocracy: participant2 added a Document to Process Title.'
    >>> send_mails[-1].body
    'participant2 added the Document "Document Title" to Process "Process Title". Visit Document: http:.../r/process/document_0000000/ .'

Added comment:

    >>> data = [
    ...     {'method': 'POST', 'path': document_path + 'comments', 'result_path': '@par1_item','result_first_version_path': '@par1_item/v1',
    ...      'body': {'content_type': IComment.__identifier__,
    ...               'data': {}}
    ...       },
    ...     {'method': 'POST', 'path': '@par1_item', 'result_path': '@par1_item/v2',
    ...      'body': {'content_type': ICommentVersion.__identifier__,
    ...               'data': {'adhocracy_core.sheets.versions.IVersionable': {
    ...                         'follows': ['@par1_item/v1']
    ...                        },
    ...                       'adhocracy_core.sheets.comment.IComment': {
    ...                         'replyto': document_path_last_version,
    ...                         'content': 'comment text'
    ...                        },
    ...               }},
    ...       },]
    >>> resp = app_participant2.batch(data)
    >>> comment_path = resp.json['responses'][0]['body']['path']
    >>> comment_path_last_version = resp.json['responses'][1]['body']['path']

   >>> send_mails[-1].subject
   'Adhocracy: participant2 added a Comment to Document Title.'
   >>> send_mails[-1].body
   'participant2 added the Comment "comment text" to Document "Document Title". Visit Comment: http:.../r/process/document_0000000/comments/comment_0000000/ .'


Updated comment:

    >>> data = {'content_type': ICommentVersion.__identifier__,
    ...         'data': {'adhocracy_core.sheets.versions.IVersionable': {
    ...                    'follows': [comment_path_last_version]
    ...                  },
    ...                  'adhocracy_core.sheets.comment.IComment': {
    ...                         'content': 'updated comment text'
    ...                  },
    ...         }}
    >>> resp = app_participant2.post(comment_path, data)
    >>> comment_path_last_version = resp.json['path']

    >>> send_mails[-1].subject
    'Adhocracy: participant2 updated Comment'
    >>> send_mails[-1].body
    'participant2 updated Comment "updated comment text". Visit Comment: http:.../r/process/document_0000000/comments/comment_0000000/ .'

Updated content:

    >>> data = {'content_type': IDocumentVersion.__identifier__,
    ...         'data': {'adhocracy_core.sheets.versions.IVersionable': {
    ...                    'follows': [document_path_last_version]
    ...                  },
    ...                  'adhocracy_core.sheets.title.ITitle': {
    ...                         'title': 'updated document title'
    ...                  },
    ...         }}
    >>> resp = app_participant2.post(document_path, data)

    >>> send_mails[-1].subject
    'Adhocracy: participant2 updated Document'
    >>> send_mails[-1].body
    'participant2 updated Document "updated document title". Visit Document: http:.../r/process/document_0000000/ .'

