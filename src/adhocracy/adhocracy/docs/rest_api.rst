Loose coupling REST-API
=======================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> import copy
    >>> from functools import reduce
    >>> import os
    >>> import requests
    >>> from pprint import pprint

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> from adhocracy.testing import settings_functional
    >>> from adhocracy import main

    >>> if 'A3_TEST_SERVER' in os.environ and os.environ['A3_TEST_SERVER']:
    ...     print('skip')
    ...     from tests.http2wsgi import http2wsgi
    ...     app = http2wsgi(os.environ['A3_TEST_SERVER'])
    ... else:
    ...     print('skip')
    ...     app = main({}, **settings_functional())
    skip...

    >>> testapp = TestApp(app)


Resource structure
------------------

Resources have one content interface to set its type, like
"adhocracy.resources.interfaces.IPool".

FIXME: rename content interface to ressource interface, this is more clear and more common
FIXME: maybe rename propertysheet interface to property interface, its shorter

Every Resource has multiple propertysheet interfaces that define schemata to set/get data.

There are 5 main types of content interfaces::

* Pool: folder content in the object hierachy, namespace, structure and configure child fusels for a specic Beteiligungsverfahren.
* Fubel: item content created during a Beteiligungsverfahren (mainly).

* FubelVersions-Pool: specific pool for all Versionable-Fubel (DAG), Tag-Fubels, and related FubelVersions-Pools
* Versionable-Fubel: Fubel with IVersionable propertysheet interface
* Tag-Fubel: Fubel with the ITag content interface, links to on or more related Versionable-Fubel

Example ressource hierarchy ::

    Pool:              categories
    Fubel:             categories/blue

    Pool:              proposals
    Versions Pool:     proposals/proposal1
    Versionable Fubel: proposals/proposal1/v1
    Tag-Fubel:         proposals/proposal1/head

    Versions Pool:     proposals/proposal1/section1
    Versionable Fubel: proposals/proposal1/section1/v1
    Tag-Fubel:         proposals/proposal1/section1/head

Basic calls
-----------

We can use the following http verbs to work with resources.


OPTIONS
~~~~~~~

Returns possible methods for this resource, example request/response data
structures and available interfaces with resource data::

    >>> resp = testapp.options("/adhocracy")
    >>> wanted =\
    ... {'GET': {'request_body': {},
    ...         'request_querystring': {},
    ...         'response_body': {'content_type': '',
    ...                           'data': {'adhocracy.properties.interfaces.IName': {},
    ...                                    'adhocracy.properties.interfaces.IPool': {}},
    ...                           'path': ''}},
    ...  'HEAD': {},
    ...  'OPTION': {},
    ...  'POST': {'request_body': [{'content_type': 'adhocracy.resources.interfaces.IFubelVersionsPool',
    ...                            'data': {'adhocracy.properties.interfaces.IName': {},
    ...                                     'adhocracy.properties.interfaces.IPool': {},
    ...                                     'adhocracy.properties.interfaces.ITags': {},
    ...                                     'adhocracy.properties.interfaces.IVersions': {}}},
    ...                           {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...                            'data': {'adhocracy.properties.interfaces.IName': {},
    ...                                     'adhocracy.properties.interfaces.IPool': {}}}],
    ...          'response_body': {'content_type': '', 'path': ''}},
    ... 'PUT': {'request_body': {'data': {'adhocracy.properties.interfaces.IName': {},
    ...                                   'adhocracy.properties.interfaces.IPool': {}}},
    ...         'response_body': {'content_type': '', 'path': ''}}}

(IName contains a path that must be a valid identifier for this resource.
The server will test its validity and reject everything that is not, say,
the path of the resource that this body was posted to plus one fresh
extra path element.  For details, see backend unit test documentation
or such.)

Semantics of read-only and mandatory flags in request body:

FIXME: the remainder of this section must be re-aligned with the actual
documentation.

*,    read-only, mandatory  => error
GET,  *,         *          => may be there (for structure selection)
*,    read-only             => must not be there
POST,            mandatory  => must be there
PUT,             mandatory  => may be there
*,               mandatory  => may be there
*,               *          => may be there

Both flags only work on a single node in the json tree, not on its
subtrees.

Possibly extra flag 'post-only': mandatory on post, read-only
afterwards (on PUT).


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

Returns resource and child elements meta data and all propertysheet interfaces with data::

    >>> resp = testapp.get("/adhocracy", )
    >>> wanted =\
    ...  {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...   'data': {'adhocracy.properties.interfaces.IName': {'name': ''},
    ...            'adhocracy.properties.interfaces.IPool': {'elements': []}},
    ...   'path': '/adhocracy'}

POST
~~~~

Create a new resource ::

    >>> prop = {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.IName': {
    ...                  'name': 'PROposals'},
    ...                  }}
    >>> resp = testapp.post_json("/adhocracy", prop)
    >>> wanted =\
    ... {
    ...    "content_type": "adhocracy.resources.interfaces.IPool",
    ...    "path": "/adhocracy/proposals
    ... }
    >>> wanted == resp.json
    True

PUT
~~~

Modify data of an existing resource ::

    >>> data = {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...         'data': {'adhocracy.properties.interfaces.IName': {'name': 'Proposals'}}}
    >>> resp = testapp.put_json("/adhocracy/proposals", data)
    >>> wanted =\
    ... {
    ...     "content_type": "adhocracy.resources.interfaces.IPool",
    ...     "path": "/adhocracy/proposals"
    ... }
    >>> wanted == resp.json
    True

Check the changed resource ::

    >>> resp = testapp.get("/adhocracy/proposals")
    >>> resp.json["data"]["adhocracy.properties.interfaces.IName"]["name"]
    "Proposals"

FIXME: write test cases for attributes with "required", "read-only",
and possibly others.  (those work the same in PUT and POST, and on any
attribute in the json tree.)


ERROR Handling
~~~~~~~~~~~~~~

The normal return code is 200 ::

    >>> data = {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...         'data': {'adhocracy.properties.interfaces.IName': {'name': 'Proposals'}}}
    >>> resp = testapp.put_json("/adhocracy/proposals", data)
    >>> resp.code
    200

If you submit invalid data the return error code is 400::

    >>> data = {'content_type': 'adhocracy.resources.interfaces.IPool',
    ...         'data': {'adhocracy.properties.interfaces.WRONGINTERFACE': {'name': 'Proposals'}}}
    >>> testapp.put_json("/adhocracy/proposals", data)
    UNEXPECTED EXCEPTION: AppError('Bad response: 400 Bad Request (not 200 OK or 3xx redirect for http://localhost/adhocracy)\n{"status": "error", "errors": [{"description": "The following propertysheets are required to create this resource: {\'adhocracy.properties.interfaces.IPool\'}", "location": "body", "name": "data"}]}',)
    ...


and you get data with a detailed error description:

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

If all goes wrong the return code is 500.


Create and Update Versionable Resources
---------------------------------------

Create
~~~~~~

Create a ProposalVersionsPool (aka FubelVersionsPool with the wanted resource type) ::

    >>> prop = {'content_type': 'adhocracy.resources.interfaces.IProposalVersionsPool',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.IName': {
    ...                  'name': 'kommunismus'},
    >>> resp = testapp.post_json("/adhocracy/proposals", prop)
    >>> proposal_versions_path = resp.json["path"]

The return data has the new attribute 'first_version_path' to get the path of the first Proposal (aka VersionableFubel)::

    >>> pprint_json(resp.json)
    {
     "content_type": "adhocracy.resources.interfaces.IProposalVersionsPool",
     "first_version_path": "/adhocracy/proposals/kommunismus/VERSION_...
     "path": "/adhocracy/proposals/kommunismus"
    }
    >>> proposal_v1_path = resp.json["first_version_path"]

The ProposalVersionsPool has the IVersions and ITags interfaces to work with Versions ::

    >>> resp = testapp.post_get(proposal_versions_path)
    >>> pprint_json(resp.json)
    ...
        "data": {
            "adhocracy.properties.interfaces.IName": {
                "name": "kommunismus"
            },
            "adhocracy.properties.interfaces.IVersions": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/VERSION_...
                ]
            }
            "adhocracy.properties.interfaces.ITags": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/TAG_FIRST"
                ]
            }
            "adhocracy.properties.interfaces.IPool": {
                "elements": []
            }

        },
    ...


Update
~~~~~~

Fetch the first Proposal Version, it is empty ::

    >>> resp = testapp.post_get(proposal_v1_path)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.resources.interfaces.IProposal",
        "data": {
            "adhocracy.properties.interfaces.INameReadOnly": {
                "name": "VERSION_...
            },
            'adhocracy.properties.interfaces.IDocument': {
                      'title': '',
                      'description': '',
                      'elements': []}}}
            "adhocracy.properties.interfaces.IPool": {
                "elements": []
            },
            "adhocracy.properties.interfaces.IVersionable": {
                "follows": [],
                "followed-by": []
            }
        },
        "path": "/adhocracy/proposals/kommunismus/VERSION_...
    }

Create a second proposal that follows the first version ::

    >>> para = {'content_type': 'adhocracy.resources.interfaces.Proposal',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.IDocument': {
    ...                  'title': 'kommunismus jetzt!',
    ...                  'description': 'blabla!',
    ...                  'elements': []}
    ...               'adhocracy.properties.Interfaces.IVersionable': {
    ...                  'follows': [proposal_v1_path],
    ...                  }
    ...          }}
    >>> resp = testapp.post_json(proposal_versions_path, para)
    >>> proposal_v2_path = resp.json["path"]
    >>> proposal_v2_path != proposal_v1_path
    True


Add and update child resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a SectionVersionsPool inside the ProposalVersionsPool::

    >>> prop = {'content_type': 'adhocracy.resources.interfaces.ISectionVersionsPool',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.IName': {
    ...              'name': 'kapitel1'},
    >>> resp = testapp.post_json(proposal_versions_path, prop)
    >>> section_versions_path = resp.json["path"]
    >>> section_v1_path = resp.json["first_version_path"]

Create a third Proposal version and add the first Section version ::

    >>> para = {'content_type': 'adhocracy.resources.interfaces.Proposal',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.IDocument': {
    ...                  'elements': [section_v1_path]}
    ...               'adhocracy.properties.Interfaces.IVersionable': {
    ...                  'follows': [proposal_v2_path],
    ...                  }
    ...          }}
    >>> resp = testapp.post_json(proposal_versions_path, para)
    >>> proposal_v3_path = resp.json["path"]


If we create a second Section version ::

    >>> prop = {'content_type': 'adhocracy.resources.interfaces.ISection',
    ...         'data': {
    ...              'adhocracy.properties.interfaces.ISection': {
    ...                  'title': 'Kapitel Überschrift Bla',
    ...                  'elements': []}
    ...               'adhocracy.properties.Interfaces.IVersionable': {
    ...                  'follows': [section_v1_path],
    ...                  }
    ...          }}
    >>> resp = testapp.post_json(sections_versions_path, prop)
    >>> section_v2_path = resp.json["path"]
    >>> section_v2_path != section_v1_path
    True

we automatically create a fourth Proposal version ::

    >>> resp = testapp.post_get(proposal_versions_path)
    >>> pprint_json(resp.json)
    ...
        "data": {
            "adhocracy.properties.interfaces.IName": {
                "name": "kommunismus"
            },
            "adhocracy.properties.interfaces.IVersions": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                ]
            }
            "adhocracy.properties.interfaces.ITags": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/TAG_FIRST"
                ]
            }
            "adhocracy.properties.interfaces.IPool": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/kapitel1"
                ]
            }
    ...

FIXME: the elements listing in the ITags interface is not very helpful, the
tag names (like "FIRST") are missing.

FIXME: should we add a Tag TAG_LAST, to reference the last added version?

FIXME: should the server tell in general where to post speccific
content interfaces? (like "like", "discussion",..)?  in other words,
should the client to be able to ask (e.g. with an OPTIONS request)
where to post a "like"?

FIXME: s/follows/predecessors/g; s/followed_by/successors/g;?


Batch requests
––––––––––––––

FIXME: eliminate talk on postroots (it's obsolete).

FIXME: one batch is one transaction: if the last request failes with a
4xx error, the entire batch request must be rolled back.  the idea
expressed in this section that half of a batch should be committed is
weird and should be dropped.

The following URL accepts POSTs of ordered sequences (json arrays) of
encoded HTTP requests in one HTTP request body ::

    >>> batch_url = '/adhocracy-batch/'

The response contains an ordered sequence of the same (or, in case of
error, shorter) length that contains the resp. HTTP responses.  First
error terminates batch processing.  Batch requests are transactional
in the sense that either all are successfully carried out or nothing
is changed on the server.

Let's add some more paragraphs to the document above ::

FIXME: postroot will go away.

    >>> batch = [ { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.resources.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
    ...                           'text': 'sein blick ist vom vorüberziehn der stäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.resources.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
    ...                           'text': 'ganz weiß geworden, so wie nicht mehr frisch' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'this is not a very well-known content-type, and will trigger an error!',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2["postroot"],
    ...             'body': { 'content_type': 'adhocracy.resources.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
    ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> pprint_json(batch_resp)
    [
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.resources.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.resources.interfaces.IParagraph",
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

    >>> propv2["data"]["adhocracy.properties.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.resources.interfaces.IParagraph', 'path': batch_resp[0]["body"]["path"]})
    ... propv2["data"]["adhocracy.properties.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.resources.interfaces.IParagraph', 'path': batch_resp[1]["body"]["path"]})
    ... propv2["data"]["adhocracy.properties.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.resources.interfaces.IParagraph', 'path': 0})
    ... propv2["data"]["adhocracy.properties.interfaces.IDocument"]["paragraphs"]
    ...      .append({ 'content_type': 'adhocracy.resources.interfaces.IParagraph', 'path': 1})
    ... propv2_vrsbl = propv2["data"]["adhocracy.properties.interfaces.IVersionable"]
    ... propv2_vrsbl["follows"] = [{'content_type': prop["content_type"], 'path': prop["path"]}]
    ... batch = [ { 'method': 'POST',
    ...             'path': prop["postroot"],
    ...             'body': { 'content_type': 'adhocracy.resources.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': prop["postroot"],
    ...             'body': { 'content_type': 'adhocracy.resources.interfaces.IParagraph',
    ...                       'data': { 'adhocracy.properties.interfaces.Text': {
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
                "content_type": "adhocracy.resources.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.resources.interfaces.IParagraph",
                "path": "..."
            }
        },
        {
            "code": 200,
            "body": {
                "content_type": "adhocracy.resources.interfaces.IProposal",
                "path": "..."
            }
        }
    ]
    >>> propv3 = testapp.get_json(batch_resp[2]["body"]["path"]).json
    {
        "content_type": "adhocracy.resources.interfaces.IProposal",
        ...
    }


Other stuff
-----------

GET /interfaces/..::

    Get schema/interface information: attribute type/required/readonly, ...
    Get interface inheritage


GET/POST /workflows/..::

    Get workflow, apply workflow to content object.


GET/POST /transitions/..::

    Get available workflow transitions for content object, execute transition.


GET /query/..::

    query catalog to find content below /instances/spd


GET/POST /users::

    Get/Add user
