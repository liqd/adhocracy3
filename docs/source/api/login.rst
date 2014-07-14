# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

User Registration and Login
===========================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> from pprint import pprint

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app_sample')
    Executin...
    >>> websocket = getfixture('websocket')
    >>> testapp = TestApp(app)


User Creation (Registration)
----------------------------

FIXME all the doctests in the document don't work yet.

A new user is registered by creating a user object under the
``/principals/users`` pool. On success, the response contains the path of
the new user.

    >>> prop = {'content_type': 'adhocracy.resources.principal.IUser',
    ...         'data': {
    ...              'adhocracy.sheets.user.UserBasicSchema': {
    ...                  'name': 'Anna Müller',
    ...                  'email': 'anna@example.org'},
    ...              'adhocracy.sheets.user.IPasswordAuthentication': {
    ...                  'password': 'EckVocUbs3'}}}
    >>> resp_data = testapp.post_json("/principals/users", prop).json
    >>> resp_data["adhocracy.resources.principal.IUser"]
    'adhocracy.resources.pool.IBasicPool'
    >>> resp_data["path"].startswith('/principals/users/')
    True

The "name" field in the "UserBasicSchema" schema is a non-empty string that
can contain any characters except '@' (to make user names distinguishable
from email addresses). The username must not contain any whitespace except
single spaces, preceded and followed by non-whitespace (no whitespace at
begin or end, multiple subsequent spaces are forbidden,
tabs and newlines are forbidden).

The "email" field must looks like a valid email address.

*Note:* for now, we **don't validate** email addresses to ensure that they
exist and really belong to the user -- email verification is part of a
future story.

Creating a new user will not automatically log them in. The frontend need to
send an explicit login request afterwards.

On failure, the backend responds with an error message. E.g. when we try to
register a user with an empty password::

    >>> prop = {'content_type': 'adhocracy.resources.principal.IUser',
    ...         'data': {
    ...              'adhocracy.sheets.user.UserBasicSchema': {
    ...                  'name': 'Anna Müllerin',
    ...                  'email': 'annina@example.org'},
    ...              'adhocracy.sheets.user.IPasswordAuthentication': {
    ...                  'password': ''}}}
    >>> resp_data = testapp.post_json("/principals/users", prop).json
    { 'status': 'error', 'errors': [...] }

<errors> is a list of errors. FIXME more on what can go wrong and how it's
reported. Tentatively, the following error conditions can happen:

  * username does already exist
  * email does already exist
  * username is invalid (e.g. contains "@", is empty, starts with
    whitespace)
  * email is invalid
  * password is too short
  * password is too long
  * password is invalid (doesn't match our arbitrary expectations, e.g.
    "password must contain an umlaut or a typographic quotation mark!")
  * internal error: something went wrong in the backend
  * anything else?

*Note:* in the future, the registration request may contain additional
personal data for the user. This data will probably be collected in one or
several additional sheets, e.g. ::

    'data': {
        'adhocracy.sheets.user.UserBasicSchema': {
            'name': 'Anna Müllerin',
            'email': 'annina@example.org'},
        'adhocracy.sheets.user.IPasswordAuthentication': {
            'password': '...'},
        'adhocracy.sheets.user.UserDetails': {
          'forename': '...',
          'surname': '...',
          'day_of_birth': '...',
          'street': '...',
          'town': '...',
          'postcode': '...',
          'gender': '...'
        }
     }


User Login
----------

To log-in an existing user via password, the frontend sends a JSON request
to the URL ``login_username`` with a user name and password::

    >>> prop = {'name': 'Anna Müllerin',
    ...         'password': 'Inawgoywyk2'}}}
    >>> resp_data = testapp.post_json('/login_username', prop).json
    >>> pprint(resp_data)
    {'status': 'success',
     'user_path': '/principals/users/...',
     'user_token': '...'
     }
    >>> user_token_via_username = resp_data['user_token']

Or to ``login_email``, specifying the user's email address instead of name::

    >>> prop = {'email': 'annina@example.org',
    ...         'password': 'Inawgoywyk2'}}}
    >>> resp_data = testapp.post_json('/login_username', prop).json
    >>> pprint(resp_data)
    {'status': 'success',
     'user_path': '/principals/users/...',
     'user_token': '...'
    }
    >>> user_token_via_email = resp_data['user_token']

On success, the backend sends back the path to the object
representing the logged-in user and a token that must be used to authorize
additional requests by the user.


User Authentication
-------------------

Once the user is logged in, the backend must add an "X-User-Token" header
field to all HTTP requests made for the user whose value is the received
"user_token". The backend validates the token. If it's valid and not
expired, the requested action is performed in the name and with the rights
of the logged-in user.

If the token is not valid or expired, the backend responds with an error
status that identifies the "X-User-Token" header as source of the problem::

    >>> headers = {'X-User-Token': 'Blah' }
    >>> resp_data = testapp.get('/meta_api/', headers=headers).json
    >>> resp_data['status']
    'error'
    >>> resp_data['errors'][0]['location']
    'header'
    >>> resp_data['errors'][0]['name']
    'X-User-Token'
    >>> resp_data['errors'][0]['description']
    'invalid user token'

Tokens will likely expire after some time. Once they are expired,
they will be considered as invalid so any further requests made by the user
will lead to errors. To resolve this, the user must log in again.


User Logout
-----------

For now, there is no explicit "logout" action that would discard a
generated user token. (*Note:* This may change in a future story.) To log a
user out, the frontend can simply "forget" the received user token and
never use it any more. The token will automatically expire in the backend
after a few hours.


User Re-Login
-------------

If a user logs in, any previous user tokens generated for the same user
will still remain valid until they expire in the normal way. This allows
the user to be logged in from different devices at the same time. ::

    >>> user_token_via_username != user_token_via_email
    True
    >>> headers = {'X-User-Token': user_token_via_username }
    >>> resp_data = testapp.get('/meta_api/', headers=headers).json
    >>> 'resources' in resp_data.keys()
    True
    >>> headers = {'X-User-Token': user_token_via_email }
    >>> resp_data = testapp.get('/meta_api/', headers=headers).json
    >>> 'resources' in resp_data.keys()
    True
