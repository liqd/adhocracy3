Adhocracy 3 loosed coupling REST-API with substance-d backend
=============================================================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> import copy
    >>> from functools import reduce
    >>> import os
    >>> import requests
    >>> from adhocracy.testing import pprint_json

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


Basic calls
-----------

We can use the following http verbs to work with resources.

OPTIONS
~~~~~~~

Returns possible methods for this resource and available interfaces
with resources data::

    >>> resp = testapp.options("/adhocracy")
    >>> pprint_json(resp.json, [['PUT'], ['GET']])
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

Returns only http headers::

    >>> resp = testapp.head("/adhocracy")
    >>> resp.headerlist # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [...('Content-Type', 'application/json; charset=UTF-8'), ...
    >>> resp.text
    ''

GET
~~~

Returns resource and child elements meta data and all interfaces with data::

    >>> resp = testapp.get("/adhocracy", )
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "data": {
            ...
            "adhocracy.propertysheets.interfaces.IName": {
                "name": ""
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "path": ...
    }

POST
~~~~

Create a new resource ::

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {
    ...                  'name': 'PROposals'},
    ...                  }}
    >>> resp = testapp.post_json("/adhocracy", prop)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "path": "/adhocracy/proposals
    }

PUT
~~~~

Modify data of an existing resource ::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {'adhocracy.propertysheets.interfaces.IName': {'name': 'Proposals'}}}
    >>> resp = testapp.put_json("/adhocracy/proposals", data)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "path": "/adhocracy/proposals"
    }

Check the changed resource::

    >>> resp = testapp.get("/adhocracy/proposals")
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IPool",
        "data": {
            ...
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "Proposals"
            },
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            }
        },
        "path": "/adhocracy/proposals"
    }

FIXME: write test cases for attributes with "required", "read-only",
and possibly others.  (those work the same in PUT and POST, and on any
attribute in the json tree.)


ERROR Handling
~~~~~~~~~~~~~~

The normal return code is 200 ::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {'adhocracy.propertysheets.interfaces.IName': {'name': 'Proposals'}}}
    >>> resp = testapp.put_json("/adhocracy/proposals", data)
    >>> resp.code
    200

If you submit invalid data

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {'adhocracy.propertysheets.interfaces.WRONGINTERFACE': {'name': 'Proposals'}}}
    >>> resp = testapp.put_json("/adhocracy/proposals", data)

the return code is 400 ::

    >>> resp.code 400

and data with a detailed error description
(like https://cornice.readthedocs.org/en/latest/validation.html?highlight=schema) ::

     {
       'status': 'error',
       'errors': errors.
     }
        With errors being a JSON dictionary with the keys “location”, “name”
        and “description”.

        location is the location of the error. It can be “querystring”,
        “header” or “body”
        name is the eventual name of the value that caused problems
        description is a description of the problem encountered.

FIXME: example error message

If all goes wrong the return code is 500.


Create and Update Versionable Resources
----------------------------------------

POST
~~~~

Create new document version and return the path ::

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.IProposal',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {
    ...                  'name': 'kommunismus jetzt!'},
    ...              'adhocracy.propertysheets.interfaces.IDocument': {
    ...                  'title': 'kommunismus jetzt!',
    ...                  'description': 'blabla!',
    ...                  'paragraphs': []}}}
    >>> resp = testapp.post_json("/adhocracy/proposals", prop)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "path": "/adhocracy/...
    }

Fetch posted document version and extract URL for POSTing updates ::

    >>> resp = testapp.get_json(resp.json["path"])
    >>> prop = resp.json
    >>> pprint_json(prop)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "data": ...
        "path": "/adhocracy/...
        "postroot": "/adhocracy/...
    }

FIXME: find technical term for things that have "postroot" and live
in "postroot"(?) and for things that initiate "postroot"(?) in
particular.  (paragraphs have a "postroot", but they live with
proposals and such.)

FIXME: should "postroot" live in a property sheet, or on top level in
the content object?

Create new paragraph and add it to proposal ::

    >>> para = {'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.INameReadOnly': {
    ...                  'name': 'kommunismus jetzt, erster abschnitt!'},
    ...              'adhocracy.propertysheets.interfaces.Text': {
    ...                  'text': 'mehr kommunismus immer blabla' }}}
    >>> resp = testapp.post_json(prop["postroot"], para)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IParagraph",
        "path": "/adhocracy/...",
        ...
    }
    >>> resp = testapp.get_json(resp.json["path"])
    >>> para = resp.json
    >>> prop["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append({'content_type': 'adhocracy.contents.interfaces.IParagraph', 'path': para["path"]})

Update versionable predecessor version and get dag-postroot:

(FIXME: s/follows/predecessors/g; s/followed_by/successors/g;?)

    >>> prop_vrsbl = prop["data"]["adhocracy.propertysheets.interfaces.IVersionable"]
    >>> prop_vrsbl["follows"] = [{'content_type': prop["content_type"], 'path': prop["path"]}]
    >>> resp = testapp.post_json(prop_vrsbl["postroot"], prop)
    >>> resp = testapp.get_json(resp.json["path"])
    >>> propv2 = resp.json
    >>> pprint_json(propv2)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "data": {
            "adhocracy.propertysheets.interfaces.IVersionable": {
                "follows": ["/adhocracy/..."],
                "postroot": "/adhocracy/...
            },
            ...
        }
        "path": "/adhocracy/...
        "postroot": "/adhocracy/...
    }

(Note: the server may handle paths like the following internally, but
the client is not supposed to worry about that:
  proposalspool/ => proposalspool/proposal1/dag/prosoal1V1
  proposalspool/proposal1/ => proposalspool/proposal1/absatz1pool/dag/absatz1V1)



Batch requests
~~~~~~~~~~~~~~

The following URL accepts POSTs of ordered sequences (json arrays) of
encoded HTTP requests in one HTTP request body ::

    >>> batch_url = '/adhocracy-batch/'

The response contains an ordered sequence of the same (or, in case of
error, shorter) length that contains the resp. HTTP responses.  First
error terminates batch processing.  Batch requests are transactional
in the sense that either all are successfully carried out or nothing
is changed on the server.

Let's add some more paragraphs to the document above ::

    >>> batch = [ { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'sein blick ist vom vorüberziehn der stäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'ganz weiß geworden, so wie nicht mehr frisch' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'this is not a very well-known content-type, and will trigger an error!',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> pprint_json(batch_resp)
    [
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.contents.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.contents.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": ...,
            "body": ...
        }
    ]

(The third element of the above array must have return code >= 400.
Not sure how to test this with doctest.)

Do this again with the last two paragraphs, but without the mistake
above.  Also throw in a request at the end that depends on the former.
References to objects earlier in the same batch request are easy:
Instead of a string that contains the URI, the 'path' field of the
reference object contains a number that points into the batch array
(numbering starts with '0').  (Numeric paths are only allowed in batch
requests!)

    >>> propv2["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.contents.interfaces.IParagraph', 'path': batch_resp[0]["body"]["path"]})
    ... propv2["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.contents.interfaces.IParagraph', 'path': batch_resp[1]["body"]["path"]})
    ... propv2["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.contents.interfaces.IParagraph', 'path': 0})
    ... propv2["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.contents.interfaces.IParagraph', 'path': 1})
    ... propv2_vrsbl = propv2["data"]["adhocracy.propertysheets.interfaces.IVersionable"]
    ... propv2_vrsbl["follows"] = [{'content_type': prop["content_type"], 'path': prop["path"]}]
    ... batch = [ { 'method': 'POST',
    ...             'path': prop["postroot"],
    ...             'body': { 'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': prop["postroot"],
    ...             'body': { 'content_type': 'adhocracy.contents.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.propertysheets.interfaces.Text': {
    ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2_vrsbl["postroot"],
    ...             'body': propv2 }
    ...         ]
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> pprint_json(batch_resp)
    [
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.contents.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.contents.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.contents.interfaces.IProposal",
                "path": "..."
            }
        }
    ]
    >>> propv3 = testapp.get_json(batch_resp[2]["body"]["path"]).json
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        ...
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

