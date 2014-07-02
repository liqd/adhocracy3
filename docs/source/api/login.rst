# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

User Registration and Login
===========================

Prerequisites
-------------

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

TODO Convert rest of document into doctest.
On failure, the backend responds with::

    { "status": "error", "errors": [<errors>] }

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
personal data for the user. This data will probably be collected in one (or
several) sheets, e.g. ::

    { "username": "<arbitrary non-empty string>",
      "email": "<e-mail address>",
      "password": "<arbitrary non-empty string>",
      "personal": {
          "forename": "...",
          "surname": "...",
          "day_of_birth": "...",
          "street": "...",
          "town": "...",
          "postcode": ..."",
          "gender": "...",
        }
    }

User Login
----------

To login an existing user via password, the frontend sends a JSON request
to the URL ``login_username`` with the following fields::

    { "username": "<arbitrary non-empty string>",
      "password": "<arbitrary non-empty string>"
    }

Or ``login_email``::

    { "email": "<e-mail address>",
      "password": "<arbitrary non-empty string>"
    }

The "username" or "email" field must contain the username/email of a
registered user and the "password" field must contain their password.

On success, the backend responds with::

   { "status": "success", 
     "user_path": "/principals/users/1" , 
     "user_token": "<arbitrary non-empty string>"
     }

User Authentication
-------------------

Once the user is logged in, the backend must add an "X-User-Token" header
field (FIXME is the name OK?) to all HTTP requests made for the user whose
value is the received "user_token". The backend validates the token. If
it's valid and not expired, the requested action is performed in the name
and with the rights of the logged-in user.

If the token is not valid or expired, the backend responds with ::

    { "status": "error",
      "errors": [
        { "location": "header",
          "name": "X-User-Token",
          "description": "invalid user token"
        }
      ]
    }

FIXME Or should we report the error in some other way?

Tokens automatically expire if they haven't been seen in any request made
during the last 3 hours. Hence, if the user and the frontend stay idle for
a longer time, the user must log in again. FIXME Or do we handle this in
some other way? Longer or shorter timespan?

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
the user to be logged in from different devices at the same time.

FIXME Or do we want to handle this situation in another way?
