Imperia API
===========

TODO: consider full post: resource + data

Preliminaries
-------------

Some imports to work with rest api calls::

    >>> from pprint import pprint
    >>> from adhocracy_core.resources.organisation import IOrganisation
    >>> from adhocracy_meinberlin.resources.bplan import IProcess
    >>> from adhocracy_core.resources.document import IDocument

Start adhocracy app and log in some users::

    >>> app_god = getfixture('app_god')
    >>> resp_data = app_god.get("/").json
    >>> app_god.base_path = '/'


Create bplan::

    >>> data = {'adhocracy_core.sheets.name.IName': {'name': 'test'}}
    >>> resp = app_god.post_resource('/', IProcess, data)
