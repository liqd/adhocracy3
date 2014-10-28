# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Abuse and Censorship
====================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> from adhocracy_core.testing import god_header

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app')
    >>> websocket = getfixture('websocket')
    >>> testapp = TestApp(app)
    >>> rest_url = 'http://localhost'

Reporting bad content
---------------------

The end point /report_abuse accepts complaint objects that consist of
a URL and a remark::

    >>> a = {'url': 'http://localhost/frontend/adhocracy',
    ...      'remark': 'i don\'t like the way this pool contains everything.'}
    >>> resp_data = testapp.post_json(rest_url + "/report_abuse", a)
    >>> resp_data.status_code
    200
    >>> resp_data.text
    ''

The 'url' is required and must be an URL managed by the frontend.
If the URL is later opened in a browser, the frontend must load and show the
resource considered offensive. The URL is thus frontend-specific; the backend
won't try to interpret it in any way.

The 'remark' is optional, it may be omitted or empty.

Censorship
----------

FIXME Move this to deletion.rst and integrate with the stuff there.

FIXME All remaining tests in this document are commented-out since the
described functionality hasn't been implemented yet!

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

FIXME: I don't know if its really a good idea to 'delete' all child
resources. This is costly and may have unwanted side effects. (joka)

FIXME Other open issues:

* Deleting can cause many modifications in other resources that have
  references/back references, but we claim that versionables are not modified.

  One option to handle this might be to leave the other resources intact,
  but responding with a special HTTP status code (e.g. 410 Gone) if the
  frontend asks for a deleted resources. In this case, the frontend would have
  to silently skip references pointing to such a "Gone" resource.

* It's not yet clear whether DELETE will only be used for "censoring"
  purposes (i.e. removal of illegitimate content) by admins, or also by normal
  users (e.g. removal of accidentally / redundantly submitted or
  obsolete content). In the latter case, the API could return the deleted
  objects if asked for -- on the other hand, it would be good to have only
  one DELETE operation that is simple to understand.
