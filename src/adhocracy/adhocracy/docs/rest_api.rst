Adhocracy 3 loosed coupling REST-API with substance-d backend
=============================================================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> import copy
    >>> from functools import reduce
    >>> import os
    >>> import requests
    >>> from pprint import pprint
    >>> import json
    >>> def show_json(obj):
    ...     return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    >>> def pprint_json(obj):
    ...     print(show_json(obj))
    >>> def sort_dict(d, sort_paths):
    ...     d2 = copy.deepcopy(d)
    ...     for path in sort_paths:
    ...         base = reduce(lambda d, seg: d[seg], path[:-1], d2)
    ...         base[path[-1]] = sorted(base[path[-1]])
    ...     return d2

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> from adhocracy.testing import config
    >>> from adhocracy import main

    >>> if 'A3_TEST_SERVER' in os.environ and os.environ['A3_TEST_SERVER']:
    ...     print('skip')
    ...     from tests.http2wsgi import http2wsgi
    ...     app = http2wsgi(os.environ['A3_TEST_SERVER'])
    ... else:
    ...     print('skip')
    ...     app = main({}, **config)
    skip...

    >>> testapp = TestApp(app)


Basic calls, working with Pool content
--------------------------------------

OPTIONS
~~~~~~~

Returns possible methods for this resource and available interfaces
with resources data::

    >>> resp = testapp.options("/adhocracy")
    >>> pprint_json(sort_dict(resp.json, [['PUT'], ['GET']]))
    {
        "GET": [
            "adhocracy.propertysheets.interfaces.IName",
            "adhocracy.propertysheets.interfaces.IPool"
        ],
        "HEAD": [],
        "POST": [
            "adhocracy.contents.interfaces.INodeContainer",
            "adhocracy.contents.interfaces.IParagraphContainer",
            "adhocracy.contents.interfaces.IPool",
            "adhocracy.contents.interfaces.IProposalContainer"
        ],
        "PUT": [
            "adhocracy.propertysheets.interfaces.IName",
            "adhocracy.propertysheets.interfaces.IPool"
        ]
    }

HEAD
~~~~

Returns only http headers for this resource::

    >>> resp = testapp.head("/adhocracy")
    >>> resp.headerlist # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [...('Content-Type', 'application/json; charset=UTF-8'), ...
    >>> resp.text
    ''

GET
~~~

Returns resource meta data, children meta data and all interfaces with data::

    >>> resp = testapp.get("/adhocracy", )
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "data": {
            "adhocracy.propertysheets.interfaces.IName": {
                "name": ""
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "path": ...
    }


PUT
~~~~

Modify and return the path of the modified resource::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {'adhocracy.propertysheets.interfaces.IName': {'name': 'NEWTITLE'}}}
    >>> resp = testapp.put_json("/adhocracy", data)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "path": "/adhocracy"
    }

Check the changed resource::

    >>> resp = testapp.get("/adhocracy")
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "data": {
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "NEWTITLE"
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "path": "/adhocracy"
    }

POST
~~~~

Create new resource and return the path::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IProposalContainer',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {'name': 'proposal1'},
    ...              'adhocracy.propertysheets.interfaces.IDag': {}}}
    >>> resp = testapp.post_json("/adhocracy", data)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IProposalContainer",
        "path": ...
    }
    >>> proposal1_path = resp.json["path"]

Checking the resource was added::

    >>> pprint_json(testapp.get(proposal1_path).json)
    {
        "content_type": "adhocracy.contents.interfaces.IProposalContainer",
        "data": {
            "adhocracy.propertysheets.interfaces.IDag": {
                "versions": [...
            },
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "proposal1"
            }
        },
        "path": ...
    }

Interfaces ::

     ..data:
        ..IContents:
            ..contents:
                ../instances/spd/w/test/p1
                ../instances/spd/w/test/p2
                .....
        ..ILikable
            ..liked:       NOTE: this can be a huge list, better use the supergraph reference search or just show a number
               ../users/1
               ../users/2
               .....

Working with Node content
-------------------------

The new IProposalContainer contains the propertysheet IDag and can be asked for
contained versions::

    >>> resp = testapp.get(proposal1_path)
    >>> inode_container_data = resp.json["data"]["adhocracy.propertysheets.interfaces.IDag"]
    >>> versions = inode_container_data["versions"]
    >>> len(versions)
    0


We create a new version, so we have to mind
the right follows relation ::

    >>> data =  {'content_type': 'adhocracy.contents.interfaces.IProposal',
    ...          'data': {'adhocracy.propertysheets.interfaces.IDocument': {
    ...                       'description': 'synopsis',
    ...                       'title': 'title'},
    ...                   'adhocracy.propertysheets.interfaces.IVersionable': {
    ...                       'follows': []}}}
    >>> resp = testapp.post_json(proposal1_path, data)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "path": ...
    }


GET /interfaces/..::

    Get schema/interface information: attribute type/required/readonly, ...
    Get interface inheritage

GET /contenttype/..::

    Get content type information

GET /supergraph/..::

    Get deps / essence_deps / essence references for content object/interface/attribute
    Get complete essence for content object

GET/POST /workflows/..::

    Get Workflow, Apply Workflow to content object,

GET/POST /transitions/..::

    Get available workflow transitions for content object, execute transition

GET /query/..::

    query catalog to find content below /instances/spd

GET/POST /users::

    Get/Add user

NOTES::

content-type and maininterface have almost the same meaning

content-urls: relative oder vollstandige URL?

users, catalog, references, ... per instance or global?

unused rest methods: DELETE

