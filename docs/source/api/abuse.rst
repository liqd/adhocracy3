# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Abuse and Censorship
====================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> import copy
    >>> from functools import reduce
    >>> from operator import itemgetter
    >>> import os
    >>> import requests
    >>> from pprint import pprint
    >>> from adhocracy_core.testing import god_header

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app')
    >>> websocket = getfixture('websocket')
    >>> testapp = TestApp(app)
    >>> rest_url = 'http://localhost'

Reporting bad content
---------------------

FIXME All tests in this document are commented-out since the described
functionality hasn't been implemented yet!

The end point /report_abuse accepts complaint objects that consist of
a URL and a remark::

    >> a = {'url': 'http://localhost/frontend/adhocracy',
    ...      'remark': 'i dont like the way this pool contains everything.'}
    >> resp_data = testapp.post_json(rest_url + "/report_abuse", a)
    >> resp_data.status_code
    200
    >> resp_data.text
    ''

If the URL is opened in a browser, the frontend must load and show the
complaint-about resource. The URL is thus frontend-specific; the backend
won't try to interpret it in any way.

Censorship
----------

Bad content can be marked as non-existent using the DELETE method.

    >> a = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...      'data': {'adhocracy_core.sheets.name.IName': {'name': 'Proposals'}}}
    >> resp_data = testapp.post_json(rest_url + "/adhocracy", a, headers=god_header)
    >> resp_data.status_code
    200
    >> resp_data = testapp.get(rest_url + "/adhocracy/Proposals").json
    >> resp_data.status_code
    200
    >> resp_data = testapp.delete(rest_url + "/adhocracy/Proposals", headers=god_header).json
    >> resp_data.status_code
    200
    >> resp_data = testapp.get(rest_url + "/adhocracy/Proposals",
    ...                        status=404).json

The authorization for 'delete' is restricted to admin roles, god, etc.
Ordinary users will never be allowed to delete anything.  (For them,
deletion will always be removal from a container.  The rest is garbage
collection.)

The backend should keep deleted objects, but never admit that they
exist over the rest api.  If a new resource is created in the place of
a deleted one, it must appear to the outside world as if there had
never been a resource.

One way to implement this is to store them as a dictionary of paths to
json objects in a file with a timestamp.

Rationale: Content may be required as evidence in legal disputes;
users may be unhappy about illegitimate deletions and the site may
wish to undo a deletion.

Deletion of dependent objects
-----------------------------

Dependent resources are implicitly deleted.  For instance, the
elements of a pool depend on the pool::

    >> a = {'content_type': 'adhocracy_core.resources.pool.IBasicPool',
    ...      'data': {'adhocracy_core.sheets.name.IName': {'name': 'Proposals'}}}
    >> resp_data = testapp.post_json(rest_url + "/adhocracy", prop, headers=god_header)
    >> resp_data.status_code
    200
    >> b = {'content_type': 'adhocracy_core.resources.sample_proposal.IProposal',
    ...      'data': {'adhocracy_core.sheets.name.IName': {'name': 'kommunismus'}}}
    >> resp_data = testapp.post_json(rest_url + "/adhocracy/Proposals", prop, headers=god_header)
    >> resp_data.status_code
    200
    >> resp_data = testapp.delete(rest_url + "/adhocracy/Proposals", headers=god_header).json
    >> resp_data.status_code
    200
    >> resp_data = testapp.get(rest_url + "/adhocracy/Proposals/kommunismus",
    ...                        status=404).json
