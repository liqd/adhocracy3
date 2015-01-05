# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Messaging
=========

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> from adhocracy_core.testing import god_header

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app')
    >>> testapp = TestApp(app)
    >>> rest_url = 'http://localhost'

User Messages
-------------

The end point '/message_user' can be used to send messages from a user to
another user or a group of users::

TODO Make test case work, preferably using manager instead of god::

    >> a = {'recipient': 'http://localhost/principals/users/0000000',
    ...      'title': 'Important notice regarding your Adhocracy account',
    ...      'text': '''Everything is fine.
    ... Thanks you for your attention and have a nice day.'''}
    >> resp_data = testapp.post_json(rest_url + "/message_user", a)
    >> resp_data.status_code
    200
    >> resp_data.text
    ''

The fields are all required and have the following semantics:

:recipient: the name of a principal, i.e. a user (`.../principals/users/...`)
    or a group of users (`.../principals/groups/...`).
:title: the title (subject) of the message. An installation-depended prefix or
    suffix may be added to the subject (e.g. "Adhocracy Notification: ...").
:text: the plain-text body of the message. An installation-depended prefix
    and/or suffix may be added to the text.

The backend checks that the user has sufficient permissions to send the
message -- only users with the *message_to_user* permission (typically granted
to the manager role) may do so. If this is the case, it sends the message per
e-mail to the specified user, or to every user in the specified group.

On success, the backend just sends an empty string back to the frontend.
Otherwise (e.g. if the user is not allowed to send messages), an error
message is send back.

TODO Add test case with insufficient permissions (using a normal user).

Messages to All
---------------

The end point '/message_all' can be used to send messages from a user to
*everybody*::

TODO Make test case work, preferably using admin instead of god::

    >> a = {'title': 'Call for participation',
    ...      'text': 'With great power comes great responsibility!'}
    >> resp_data = testapp.post_json(rest_url + "/message_all", a)
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

TODO Add test case with insufficient permissions (using a manager).
