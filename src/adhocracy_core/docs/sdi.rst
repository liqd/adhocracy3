# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

Substanced Admin interface (sdi)
================================

A generic admin interface is provided based on :mod:`substanced.sdi`.

First you have to start adhocracy

    >>> from webtest import TestApp
    >>> app_router = getfixture('app_router')
    >>> testapp = TestApp(app_router)
    >>> manage_url = 'http://localhost/manage'

You have to login first::

    >>> resp = testapp.get(manage_url)
    >>> csrf = resp.html.input['value']
    >>> data = {'login': 'god',
    ...         'password': 'password',
    ...         'csrf_token': csrf,
    ...         'form.submitted': 'Log In'}
    >>> resp = testapp.post(manage_url + '/@@login', data)

then you are redirected to the sdi contents listing::

    >>> resp.location
    '.../manage'
    >>> resp = testapp.get(resp.location)
    >>> resp.location
    '.../manage/@@contents'
    >>> resp = testapp.get(resp.location)
    >>> '/adhocracy/@@manage_main' in resp.text
    True
