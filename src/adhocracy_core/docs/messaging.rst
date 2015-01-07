# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Messaging
=========

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> from adhocracy_core import testing

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app')
    >>> testapp = TestApp(app)
    >>> rest_url = 'http://localhost'

Message to a User
-----------------

The end point '/message_user' can be used to send messages from a user to
another user or a group of users::

    >>> a = {'recipient': 'http://localhost/principals/users/0000000',
    ...      'title': 'Important notice regarding your Adhocracy account',
    ...      'text': '''Everything is fine.
    ... Thank you for your attention and have a nice day.'''}
    >>> resp_data = testapp.post_json(rest_url + "/message_user", a,
    ...                              headers=testing.contributor_header)
    >>> resp_data.status_code
    200
    >>> resp_data.text
    ''

The fields are all required and have the following semantics:

:recipient: the name of a user (`.../principals/users/...`)
:title: the title (subject) of the message. An installation dependent prefix or
    suffix may be added to the subject (e.g. "Adhocracy Notification: ...").
:text: the plain-text body of the message. An installation dependent prefix
    and/or suffix may be added to the text.

The backend checks that the user has sufficient permissions to send the
message -- only users with the *message_to_user* permission (typically granted
to the contributor role) may do so. If this is the case, it sends the message
per e-mail to the specified user, or to every user in the specified group.

On success, the backend just sends an empty string back to the frontend.
Otherwise (e.g. if the user is not allowed to send messages), an error
message is sent back.

If a user doesn't have the necessary permissions (e.g. because they are not
logged in), the backend responds with 403 Forbidden::

    >>> a = {'recipient': 'http://localhost/principals/users/0000000',
    ...      'title': 'Important notice regarding your Adhocracy account',
    ...      'text': '''Everything is fine.
    ... Thanks you for your attention and have a nice day.'''}
    >>> resp_data = testapp.post_json(rest_url + "/message_user", a,
    ...                               status=403)


Message to a Group of User
--------------------------

FIXME In the future, it'll be possible to send messages to groups of users,
using the end point '/message_group'. The end point works just like
'/message_user', except that the *recipient* is a group
(`.../principals/groups/...`) instead of a single user. This requires the
*message_to_group* permission, typically granted to the manager role.
The message is sent per e-mail to every user in the specified group.
This is not yet implemented because we haven't needed it yet.


Messages to All
---------------

FIXME The following is not implemented yet. Also, it will probably be
implemented via an internal messaging system rather then by sending mails to
everyone.

The end point '/message_all' can be used to send messages from a user to
*everybody*::

    >> a = {'title': 'Call for participation',
    ...      'text': 'With great power comes great responsibility!'}
    >> resp_data = testapp.post_json(rest_url + "/message_all", a,
    ...                              headers=testing.admin_header)
    >> resp_data.status_code
    200
    >> resp_data.text
    ''

The fields are both required and have the same semantics as above.

The backend checks that the user has sufficient permissions to send the
message -- only users with the *message_to_all* permission (typically granted
to the admin role) may do so. If this is the case, it sends the message per
e-mail to *all* users registered at the Adhocracy installation, so this
function should really be used with care!

The backend responds with an empty string or an error message, as above.

FIXME Add test case with insufficient permissions::

    >> a = {'title': 'Call for participation',
    ...      'text': 'With great power comes great responsibility!'}
    >> resp_data = testapp.post_json(rest_url + "/message_all", a,
    ...                headers=testing.manager_header, status=403)
