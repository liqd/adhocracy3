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

See :doc:`deletion` for an example of hiding (censoring) bad content.
