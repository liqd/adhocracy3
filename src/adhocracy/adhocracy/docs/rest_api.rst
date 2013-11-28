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


Resource structure
------------------

Resources have one content interface to set its type, like
"adhocracy.contents.interfaces.IPool".

FIXME: rename content interface to ressource interface, this is more clear and more common
FIXME: maybe rename propertysheet interface to property interface, its shorter

Every Resource has multiple propertysheet interfaces that define schemata to set/get data.

There are 5 main types of content interfaces::

* Pool: folder content in the object hierachy, namespace, structure and configure child fusels for a specic Beteiligungsverfahren.
* Fubel: item content created during a Beteiligungsverfahren (mainly).

* FubelVersions-Pool: specific pool for all Versionable-Fubel (DAG), Tag-Fubels, and related FubelVersions-Pools
* Versionable-Fubel: Fubel with IVersionable propertysheet interface
* Tag-Fubel: Fubel with the ITag content interface, links to on or more related Versionable-Fubel

Example ressource hierarchy:

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
            "adhocracy.contents.interfaces.IPool",
            "adhocracy.contents.interfaces.IProposalVersionsPool"
        ],
        "PUT": [
            "adhocracy.propertysheets.interfaces.IName",
            "adhocracy.propertysheets.interfaces.IPool"
        ]
    }

FIXME: IName property sheet will go away.  It used to be an
unambiguous object identifier, but the path is already good for that.
It was also confusingly abused as a human-readable descriptor for the
object, which is somewhat useful, but also useful in references, not
just in objects.  It was decided that IName will be removed and
replaced by an optional field "name" next to "content_type", "path",
and "data".


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

FIXME: Was bedeutet das IName interface, ist das die id aus der die URL
erzeugt wird?


PUT
~~~

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

and you get data with a detailed error description
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
---------------------------------------

Create
~~~~~~

Create a ProposalVersionsPool (aka FubelVersionsPool with the wanted resource type) ::

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.IProposalVersionsPool',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {
    ...                  'name': 'kommunismus'},
    >>> resp = testapp.post_json("/adhocracy/proposals", prop)
    >>> proposal_versions_path = resp.json["path"]

The return data has the new attribute 'first_version_path' to get the path of the first Proposal (aka VersionableFubel)::

    >>> pprint_json(resp.json)
    {
     "content_type": "adhocracy.contents.interfaces.IProposalVersionsPool",
     "first_version_path": "/adhocracy/proposals/kommunismus/VERSION_...
     "path": "/adhocracy/proposals/kommunismus"
    }
    >>> proposal_v1_path = resp.json["first_version_path"]

The ProposalVersionsPool has the IVersions and ITags interfaces to work with Versions ::

    >>> resp = testapp.post_get(proposal_versions_path)
    >>> pprint_json(resp.json)
    ...
        "data": {
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "kommunismus"
            },
            "adhocracy.propertysheets.interfaces.IVersions": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/VERSION_...
                ]
            }
            "adhocracy.propertysheets.interfaces.ITags": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/TAG_FIRST"
                ]
            }
            "adhocracy.propertysheets.interfaces.IPool": {
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
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "data": {
            "adhocracy.propertysheets.interfaces.INameReadOnly": {
                "name": "VERSION_...
            },
            'adhocracy.propertysheets.interfaces.IDocument': {
                      'title': '',
                      'description': '',
                      'elements': []}}}
            "adhocracy.propertysheets.interfaces.IPool": {
                "elements": []
            },
            "adhocracy.propertysheets.interfaces.IVersionable": {
                "follows": [],
                "followed-by": []
            }
        },
        "path": "/adhocracy/proposals/kommunismus/VERSION_...
    }

Create a second proposal that follows the first version ::

    >>> para = {'content_type': 'adhocracy.contents.interfaces.Proposal',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IDocument': {
    ...                  'title': 'kommunismus jetzt!',
    ...                  'description': 'blabla!',
    ...                  'elements': []}
    ...               'adhocracy.propertysheets.Interfaces.IVersionable': {
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

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.ISectionVersionsPool',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {
    ...              'name': 'kapitel1'},
    >>> resp = testapp.post_json(proposal_versions_path, prop)
    >>> section_versions_path = resp.json["path"]
    >>> section_v1_path = resp.json["first_version_path"]

Create a third Proposal version and add the first Section version ::

    >>> para = {'content_type': 'adhocracy.contents.interfaces.Proposal',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IDocument': {
    ...                  'elements': [section_v1_path]}
    ...               'adhocracy.propertysheets.Interfaces.IVersionable': {
    ...                  'follows': [proposal_v2_path],
    ...                  }
    ...          }}
    >>> resp = testapp.post_json(proposal_versions_path, para)
    >>> proposal_v3_path = resp.json["path"]


If we create a second Section version ::

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.ISection',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.ISection': {
    ...                  'title': 'Kapitel Überschrift Bla',
    ...                  'elements': []}
    ...               'adhocracy.propertysheets.Interfaces.IVersionable': {
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
            "adhocracy.propertysheets.interfaces.IName": {
                "name": "kommunismus"
            },
            "adhocracy.propertysheets.interfaces.IVersions": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                    "/adhocracy/proposals/kommunismus/VERSION..."
                ]
            }
            "adhocracy.propertysheets.interfaces.ITags": {
                "elements": [
                    "/adhocracy/proposals/kommunismus/TAG_FIRST"
                ]
            }
            "adhocracy.propertysheets.interfaces.IPool": {
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
