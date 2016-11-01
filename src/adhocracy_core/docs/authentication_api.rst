# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

User Registration and Login
===========================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> from copy import copy
    >>> from pprint import pprint
    >>> from adhocracy_core.testing import broken_header

Start adhocracy app and log in some users::

    >>> anonymous = getfixture('app_anonymous')
    >>> participant = getfixture('app_participant')
    >>> moderator = getfixture('app_moderator')
    >>> admin = getfixture('app_admin')
    >>> log = getfixture('log')

Test that the relevant resources and sheets exist:

    >>> resp = anonymous.get("http://localhost/meta_api/").json
    >>> 'adhocracy_core.sheets.versions.IVersions' in resp['sheets']
    True
    >>> 'adhocracy_core.sheets.principal.IUserBasic' in resp['sheets']
    True
    >>> 'adhocracy_core.sheets.principal.IUserExtended' in resp['sheets']
    True
    >>> 'adhocracy_core.sheets.principal.IPasswordAuthentication' in resp['sheets']
    True

User Creation (Registration)
----------------------------

A new user is registered by creating a user object under the
``/principals/users`` pool. On success, the response contains the
path of the new user::

    >>> data = {'content_type': 'adhocracy_core.resources.principal.IUser',
    ...         'data': {
    ...              'adhocracy_core.sheets.principal.IUserBasic': {
    ...                  'name': 'Anna Müller'},
    ...              'adhocracy_core.sheets.principal.IUserExtended': {
    ...                  'email': 'anna@example.org'},
    ...              'adhocracy_core.sheets.principal.IPasswordAuthentication': {
    ...                  'password': 'EckVocUbs3'}}}
    >>> resp = anonymous.post("http://localhost/principals/users", data).json
    >>> resp["content_type"]
    'adhocracy_core.resources.principal.IUser'
    >>> user_path = resp["path"]
    >>> user_path
    '.../principals/users/00...

The "name" field in the "IUserBasic" schema is a non-empty string that
can contain any characters except '@' (to make user names distinguishable
from email addresses). The username must not contain any whitespace except
single spaces, preceded and followed by non-whitespace (no whitespace at
begin or end, multiple subsequent spaces are forbidden,
tabs and newlines are forbidden).

The "email" field in the "IUserExtended" sheet must be a valid email address.

Creating a new user will not automatically log them in. First, the backend
will send a registration message to the specified email address. Once the user
has clicked on the activation link in the message, the user account is ready
to be used (see "Account Activation" below).

On failure, the backend responds with status code 400 and an error message.
E.g. when we try to register a user with an empty password::

    >>> data = {'content_type': 'adhocracy_core.resources.principal.IUser',
    ...         'data': {
    ...              'adhocracy_core.sheets.principal.IUserBasic': {
    ...                  'name': 'Other User'},
    ...              'adhocracy_core.sheets.principal.IUserExtended': {
    ...                  'email': 'annina@example.org'},
    ...              'adhocracy_core.sheets.principal.IPasswordAuthentication': {
    ...                  'password': ''}}}
    >>> resp = anonymous.post('http://localhost/principals/users', data)
    >>> resp.status_code
    400
    >>> pprint(resp.json)
    {'errors': [{'description': 'Required',
                 'location': 'body',
                 'name': 'data.adhocracy_core.sheets.principal.IPasswordAuthentication.password'}],
     'status': 'error'}

<errors> is a list of errors. The above error indicates that a required
field (the password field) is missing or empty. The following other error
conditions can occur:

  * username does already exist
  * email does already exist
  * email is invalid (doesn't look like an email address)
  * couldn't send a registration mail to the email address (description
    starts with 'Cannot send registration mail')
  * password is too short (less than 6 chars)
  * password is too long (more than 100 chars)
  * internal error: something went wrong in the backend

For example, if we try to register a user whose email address is already
registered::

    >>> data = {'content_type': 'adhocracy_core.resources.principal.IUser',
    ...         'data': {
    ...              'adhocracy_core.sheets.principal.IUserBasic': {
    ...                  'name': 'New user with old email'},
    ...              'adhocracy_core.sheets.principal.IUserExtended': {
    ...                  'email': 'anna@example.org'},
    ...              'adhocracy_core.sheets.principal.IPasswordAuthentication': {
    ...                  'password': 'EckVocUbs3'}}}
    >>> resp = anonymous.post('http://localhost/principals/users', data)
    >>> resp.status_code
    400
    >>> pprint(resp.json)
    {'errors': [{'description': 'The user login email is not unique',
                 'location': 'body',
                 'name': 'data.adhocracy_core.sheets.principal.IUserExtended.email'}],
     'status': 'error'}

*Note:* in the future, the registration request may contain additional
personal data for the user. This data will probably be added to the
"IUserBasic" sheets, if it's generally public, to the "IUserExtended" sheet
otherwise (or maybe it'll be store in additional new sheets); e.g.::

    'data': {
        'adhocracy_core.sheets.principal.IUserBasic': {
            'name': 'Anna Müller',
            'forename': '...',
            'surname': '...'},
        'adhocracy_core.sheets.principal.IPasswordAuthentication': {
            'password': '...'},
        'adhocracy_core.sheets.principal.IUserExtended': {
            'email': 'anna@example.org',
            'day_of_birth': '...',
            'street': '...',
            'town': '...',
            'postcode': '...',
            'gender': '...'
        }
     }


Account Activation
------------------

Before they have confirmed their email address, new users are invisible
(hidden). They won't show up in user listings, and retrieving information
about them manually leads to a *410 Gone* response (see :doc:`deletion`)::

    >>> resp = anonymous.get(user_path)
    >>> resp.status_code
    410
    >>> resp.json['reason']
    'hidden'

On user registration, the backend sends a mail with an activation link
to the specified email address and sends a 2xx HTTP response to the
frontend, so the frontend can tell the user to expect an email.  The
user has to click on the activation link to activate their
account. The *path* component of all such links starts with
``/activate/``. Once the frontend receives a click on such a link, it
must post a JSON request containing the path to the
``activate_account`` endpoint of the backend::

    >>> newest_activation_path = getfixture('newest_activation_path')
    >>> data = {'path': newest_activation_path}
    >>> resp = anonymous.post('http://localhost/activate_account', data).json
    >>> pprint(resp)
    {'status': 'success',
     'user_path': '.../principals/users/...',
     'user_token': '...'}

The backend responds with either response code 200 and 'status':
'success' and 'user_path' and 'user_token', just like after a
successful login request (see next section).  This means that the user
account has been activated and the user is now logged in. ::

    >>> data = {'path': '/activate/blahblah'}
    >>> resp = anonymous.post('http://localhost/activate_account', data)
    >>> resp.status_code
    400
    >>> pprint(resp.json)
    {'errors': [{'description': 'Unknown or expired activation path',
                 'location': 'body',
                 'name': 'path'}],
     'status': 'error'}

Or it responds with response code 400 and 'status': 'error'. Usually the error
description will be one of:

* 'String does not match expected pattern' if the path doesn't start with
  '/activate/'
* 'Unknown or expired activation path' if the activation path is unknown to
  the backend or if it has expired because it was generated more
  than 7 days ago. Note that activation links are deleted from the backend
  once the account has been successfully activated, and expired links may
  also be deleted. Therefore we don't know whether the activation link was
  never valid (the user mistyped it or just tried to guess one), or it used
  to be valid but has expired. The message displayed to the user should
  explain that.

If the link is expired, user activation is no longer possible for security
reasons and the user has to call support or register again, using a different
email. (More user-friendly options are planned but haven't been implemented
yet!)

Since the user account has been activated, the public part of the user
information is now visible to everybody::

    >>> resp = anonymous.get(user_path).json
    >>> resp['data']['adhocracy_core.sheets.principal.IUserBasic']['name']
    'Anna Müller'

Like every resource, the user has a metadata sheet with creation information.
In the case of users, the creator is the user themselves::

    >>> resp_metadata = resp['data']['adhocracy_core.sheets.metadata.IMetadata']
    >>> resp_metadata['creator']
    '.../principals/users/00...
    >>> resp_metadata['creator'] == user_path
    True


User Login
----------

To log-in an existing and activated user via password, the frontend posts a
JSON request to the URL ``login_username`` with a user name and password::

    >>> data = {'name': 'Anna Müller',
    ...         'password': 'EckVocUbs3'}
    >>> resp = anonymous.post('http://localhost/login_username', data).json
    >>> pprint(resp)
    {'status': 'success',
     'user_path': '.../principals/users/...',
     'user_token': '...'}
    >>> user_path = resp['user_path']
    >>> user_token_via_username = resp['user_token']
    >>> headers = {'X-User-Token': user_token_via_username}
    >>> user = copy(anonymous)
    >>> user.header = headers

Or to ``login_email``, specifying the user's email address instead of name::

    >>> data = {'email': 'anna@example.org',
    ...        'password': 'EckVocUbs3'}
    >>> resp = anonymous.post('http://localhost/login_email', data).json
    >>> pprint(resp)
    {'status': 'success',
     'user_path': '.../principals/users/...',
     'user_token': '...'}
    >>> user_token_via_email = resp['user_token']

On success, the backend sends back the path to the object
representing the logged-in user and a token that must be used to authorize
additional requests by the user.

An error is returned if the specified user name or email doesn't exist or if
the wrong password is specified. For security reasons, the same error message
(referring to the password) is given in all these cases::

    >>> data = {'name': 'No such user',
    ...         'password': 'EckVocUbs3'}
    >>> resp = anonymous.post('http://localhost/login_username', data)
    >>> resp.status_code
    400
    >>> pprint(resp.json)
    {'errors': [{'description': "User doesn't exist or password is wrong",
                 'location': 'body',
                 'name': 'password'}],
     'status': 'error'}

A different error message is given if username and password are valid but
the user account hasn't been activated yet::

    {"description": "User account not yet activated",
     "location": "body",
     "name": "name"}


User Authentication
-------------------

Once the user is logged in, the backend must add add header field to all
HTTP requests made for the user: "X-User-Token". Its value
is the received "user_token",
respectively. The backend validates the token. If it's valid and not
expired, the requested action is performed in the name and with the rights
of the logged-in user.

Without authentication we may not post anything::

    >>> resp = anonymous.options("/").json
    >>> 'POST' not in resp
    True

With authentication instead we may::

    >>> resp = admin.options("/").json
    >>> pprint(resp['POST']['request_body'])
    [...'adhocracy_core.resources.organisation.IOrganisation',...]

If the token is not valid or expired the backend responds with an error status
that identifies the "X-User-Token" header as source of the problem::

    >>> broken = copy(anonymous)
    >>> broken.header = broken_header
    >>> resp = broken.get('http://localhost/meta_api/')
    >>> resp.status_code
    400
    >>> sorted(resp.json.keys())
    ['errors', 'status']
    >>> resp.json['status']
    'error'
    >>> resp.json['errors'][0]['location']
    'header'
    >>> resp.json['errors'][0]['name']
    'X-User-Token'
    >>> resp.json['errors'][0]['description']
    'Invalid user token'
    >>> anonymous.header = {}

Tokens will usually expire after some time. (In the current implementation,
they expire by default after 30 days, but configurations may change this.)
Once they are expired, they will be considered as invalid so any further
requests made by the user will lead to errors. To resolve this,
the user must log in again.

Viewing Users
-------------

Without authorization, only very limited information on each user is
visible::

    >>> resp = anonymous.get(user_path).json
    >>> resp['data']['adhocracy_core.sheets.principal.IUserBasic']
    {'name': 'Anna Müller'}
    >>> 'adhocracy_core.sheets.principal.IUserExtended' in resp['data']
    False
    >>> 'adhocracy_core.sheets.principal.IPermissions' in resp['data']
    False

Only admins and the user herself can view extended information such as her
email address::

    >>> resp = admin.get(user_path).json
    >>> pprint(resp['data']['adhocracy_core.sheets.principal.IUserExtended'])
    {'email': 'anna@example.org', 'tzname': 'UTC'}
    >>> 'adhocracy_core.sheets.principal.IPermissions' in resp['data']
    True
    >>> resp = user.get(user_path).json
    >>> 'adhocracy_core.sheets.principal.IUserExtended' in resp['data']
    True
    >>> 'adhocracy_core.sheets.principal.IPermissions' in resp['data']
    True

Other users, even if logged in, cannot::

    >>> resp = participant.get(user_path).json
    >>> 'adhocracy_core.sheets.principal.IUserExtended' in resp['data']
    False
    >>> 'adhocracy_core.sheets.principal.IPermissions' in resp['data']
    False


Editing Users
-------------

User can edit their own data::

    >>> headers = {'X-User-Token': user_token_via_username}
    >>> user = copy(anonymous)
    >>> user.header = headers
    >>> data = {'data': {'adhocracy_core.sheets.principal.IUserBasic': {'name': 'edited_name'}}}
    >>> resp = user.put(user_path, data).json
    >>> len(resp['updated_resources']['modified'])
    1

If they want to edit security-related information they need to pass
their passwords in a custom header::

    >>> headers = {'X-User-Token': user_token_via_username,
    ...            'X-User-Password': 'EckVocUbs3'}
    >>> user = copy(anonymous)
    >>> user.header = headers
    >>> data = {'data': {'adhocracy_core.sheets.principal.IPasswordAuthentication': {'password': 'edited_password'}}}
    >>> resp = user.put(user_path, data).json
    >>> len(resp['updated_resources']['modified'])
    1

If the header is missing the change is silently dropped::

    >>> headers = {'X-User-Token': user_token_via_username}
    >>> user = copy(anonymous)
    >>> user.header = headers
    >>> data = {'data': {'adhocracy_core.sheets.principal.IPasswordAuthentication': {'password': 'edited_password'}}}
    >>> resp = user.put(user_path, data).json
    >>> len(resp['updated_resources']['modified'])
    0


Password Reset
--------------

If users forget their passwords, they can request a reset email::

    >>> data = {'email': 'anna@example.org'}
    >>> resp = anonymous.post('http://localhost/create_password_reset', data).json
    >>> resp['status']
    'success'

The email contains a link that will allow them to enter a new password.
Password reset also returns the credentials so that a user can login
directly::

    >>> newest_reset_path = getfixture('newest_reset_path')
    >>> data = {'path': newest_reset_path(),
    ...         'password': 'new_password'}
    >>> resp = anonymous.post("http://localhost/password_reset", data).json
    >>> pprint(resp)
    {'status': 'success',
     'user_path': '.../principals/users/...',
     'user_token': '...'}
