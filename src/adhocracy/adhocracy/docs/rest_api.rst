# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

REST-API (with loose coupling)
===============================

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
"adhocracy.resources.pool.IBasicPool".

FIXME: rename content interface to ressource interface, this is more clear and more common
FIXME: maybe rename propertysheet interface to property interface, its shorter

Every Resource has multiple propertysheet interfaces that define schemata to set/get data.

There are 5 main types of content interfaces:

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

    >>> resp_data = testapp.options("/adhocracy").json
    >>> sorted(resp_data.keys())
    ['GET', 'HEAD', 'OPTION', 'POST', 'PUT']

    >>> sorted(resp_data["GET"]["response_body"]["data"].keys())
    ['adhocracy.sheets.name.IName', 'adhocracy.sheets.pool.IPool']

    >>> sorted(resp_data["PUT"]["request_body"]["data"].keys())
    ['adhocracy.sheets.name.IName']

The value for POST gives us list with valid request data stubs::

    >>> data_post_pool = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...                   'data': {'adhocracy.sheets.name.IName': {}}}
    >>> data_post_pool in resp_data["POST"]["request_body"]
    True

  (IName contains a path that must be a valid identifier for this resource.
The server will test its validity and reject everything that is not, say,
the path of the resource that this body was posted to plus one fresh
extra path element.  For details, see backend unit test documentation
or such.)

Semantics of read-only and mandatory flags in request body:


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

    >>> resp_data = testapp.get("/adhocracy").json
    >>> pprint(resp_data["data"])
    {'adhocracy.sheets.name.IName': {'name': 'adhocracy'},
     'adhocracy.sheets.pool.IPool': {'elements': []}}

POST
~~~~

Create a new resource ::

    >>> prop = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...         'data': {
    ...              'adhocracy.sheets.name.IName': {
    ...                  'name': 'Proposals'}}}
    >>> resp_data = testapp.post_json("/adhocracy", prop).json
    >>> resp_data["content_type"]
    'adhocracy.resources.pool.IBasicPool'
    >>> resp_data["path"]
    '/adhocracy/Proposals'

PUT
~~~

Modify data of an existing resource ::

    >>> data = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'proposals'}}}
    >>> resp_data = testapp.put_json("/adhocracy/Proposals", data).json
    >>> pprint(resp_data)
    {'content_type': 'adhocracy.resources.pool.IBasicPool',
     'path': '/adhocracy/Proposals'}

Check the changed resource ::

    >>> resp_data = testapp.get("/adhocracy/Proposals").json
    >>> resp_data["data"]["adhocracy.sheets.name.IName"]["name"]
    'proposals'

FIXME: write test cases for attributes with "required", "read-only",
and possibly others.  (those work the same in PUT and POST, and on any
attribute in the json tree.)


ERROR Handling
~~~~~~~~~~~~~~

FIXME: ... is not working anymore in this doctest

The normal return code is 200 ::

    >>> data = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'Proposals'}}}

.. >>> testapp.put_json("/adhocracy/Proposals", data)
.. 200 OK application/json ...

If you submit invalid data the return error code is 400::

    >>> data = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...         'data': {'adhocracy.sheets.example.WRONGINTERFACE': {'name': 'Proposals'}}}

.. >>> testapp.put_json("/adhocracy/Proposals", data)
.. Traceback (most recent call last):
.. ...
.. {"errors": [{"description": ...

and you get data with a detailed error description::

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


Introduction and Motivation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section explains updates to resources with version control.  Two
property sheets are central to version control in adhocracy: IDAG and
IVersion.  IVersion is in all content objects that support version
control, and IDAG is a container that manages all versions of a
particular content object in a directed acyclic graph.

IDAG content objects as well as IVersion objects need to be created
explicitly by the frontend.

The server supports updating a content object that implements IVersion by
letting you post a content object with missing IVersion property sheet
to the DAG (IVersion is read-only and managed by the server), and
passing a list of parent versions in the post parameters of the
request.  If there is only one parent version, the new version either
forks off an existing branch or just continues a linear history.  If
there are several parent versions, we have a merge commit.

Example: If a new versionable content object has been created by the
user, the front-end first posts an IDAG.  The IDAG works a little like
an IPool in that it allows posting versions to it.  The front-end will
then simply post the initial version into the IDAG with an empty
predecessor version list.

IDAG content objects may also implement the IPool property sheet for
containing further IDAG content objects for sub-structures of
structured versionable content types.  Example: A document may consist
of a title, description, and a list of references to sections.
There is a DAG for each document and each such dag contains one DAG
for each section that occurs in any version of the document.
Section refs in the document object point to specific versions in
those DAGs.

When posting updates to nested sub-structures, the front-end must
decide for which parent objects it wants to trigger an update.  To
stay in the example above: If we have a document with two sections,
and update a section, the post request must contain both the parent
version(s) of the section, but also the parent version(s) of the
document that it is supposed to update.

To see why, consider the following situation::

    Doc     v0       v1      v2
                    /       /
    Par1    v0    v1       /
                          /
    Par2    v0          v1

          >-----> time >-------->

We want Doc to be available in 3 versions that are linearly dependent
on each other.  But when the update to Par2 is posted, the server has
no way of knowing that it should update v1 of Doc, BUT NOT v0!


Create
~~~~~~

Create a ProposalVersionsPool (aka FubelVersionsPool with the wanted resource type) ::

    >>> prop = {'content_type': 'adhocracy.resources.proposal.IProposalVersionsPool',
    ...         'data': {
    ...              'adhocracy.sheets.name.IName': {
    ...                  'name': 'kommunismus'}
    ...              }
    ...         }
    >>> resp = testapp.post_json("/adhocracy/Proposals", prop)
    >>> proposal_versions_path = resp.json["path"]
    >>> proposal_versions_path
    '/adhocracy/Proposals/kommunismus'

The return data has the new attribute 'first_version_path' to get the path first Version::

    >>> proposal_v1_path = resp.json['first_version_path']
    >>> proposal_v1_path
    '/adhocracy/Proposals/kommunismus/VERSION_0000000'

Version IDs are numeric and assigned by the server.  The front-end has
no control over them, and they are not supposed to be human-memorable.
For human-memorable version pointers that also allow for complex
update behavior (fixed-commit, always-newest, ...), consider property
sheet ITags.

The ProposalVersionsPool has the IVersions and ITags interfaces to work with Versions::

    >>> resp = testapp.get(proposal_versions_path)
    >>> resp.json['data']['adhocracy.sheets.versions.IVersions']['elements']
    ['/adhocracy/Proposals/kommunismus/VERSION_0000000']

    >>> resp.json['data']['adhocracy.sheets.tags.ITags']['elements']
    ['/adhocracy/Proposals/kommunismus/FIRST', '/adhocracy/Proposals/kommunismus/LAST']

Update
~~~~~~

Fetch the first Proposal Version, it is empty ::

    >>> resp = testapp.get(proposal_v1_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.document.IDocument'])
    {'description': '', 'elements': [], 'title': ''}

    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersionable'])
    {'follows': []}

Create a second proposal that follows the first version ::

    >>> para = {'content_type': 'adhocracy.resources.proposal.IProposal',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'title': 'kommunismus jetzt!',
    ...                     'description': 'blabla!',
    ...                     'elements': []},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [proposal_v1_path]}
    ...             }}
    >>> resp = testapp.post_json(proposal_versions_path, para)
    >>> proposal_v2_path = resp.json["path"]
    >>> proposal_v2_path != proposal_v1_path
    True


Add and update child resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a SectionVersionsPool inside the ProposalVersionsPool::

    >>> prop = {'content_type': 'adhocracy.resources.section.ISectionVersionsPool',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel1'},}
    ...         }
    >>> resp = testapp.post_json(proposal_versions_path, prop)
    >>> section_versions_path = resp.json["path"]
    >>> section_v1_path = resp.json["first_version_path"]

Create a third Proposal version and add the first Section version ::

    >>> para = {'content_type': 'adhocracy.resources.proposal.IProposal',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'elements': [section_v1_path]},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [proposal_v2_path],}
    ...                 }}
    >>> resp = testapp.post_json(proposal_versions_path, para)
    >>> proposal_v3_path = resp.json["path"]


If we create a second Section version ::

    >>> prop = {'content_type': 'adhocracy.resources.section.ISection',
    ...         'data': {
    ...              'adhocracy.sheets.document.ISection': {
    ...                  'title': 'Kapitel Überschrift Bla',
    ...                  'elements': []},
    ...               'adhocracy.sheets.versions.IVersionable': {
    ...                  'follows': [section_v1_path],
    ...                  }
    ...          }}
    >>> resp = testapp.post_json(section_versions_path, prop)
    >>> section_v2_path = resp.json['path']
    >>> section_v2_path != section_v1_path
    True

we automatically create a fourth Proposal version ::

    >>> resp = testapp.get(proposal_versions_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersions'])
    {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000000',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000001',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000002',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000003']}

FIXME: the elements listing in the ITags interface is not very helpful, the
tag names (like 'FIRST') are missing.

FIXME: should we add a Tag TAG_LAST, to reference the last added version?

FIXME: should the server tell in general where to post speccific
content interfaces? (like 'like', 'discussion',..)?  in other words,
should the client to be able to ask (e.g. with an OPTIONS request)
where to post a 'like'?

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
    ...             'path': propv2['postroot'],
    ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'sein blick ist vom vorüberziehn der stäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2['postroot'],
    ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'ganz weiß geworden, so wie nicht mehr frisch' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2['postroot'],
    ...             'body': { 'content_type': 'this is not a very well-known content-type, and will trigger an error!',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2['postroot'],
    ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> pprint(batch_resp)
    [
        {
            'code': 200,
            'body': {
                'content_type': 'adhocracy.resources.IParagraph',
                'path': '...'
            }
        },
        {
            'code': 200,
            'body': {
                'content_type': 'adhocracy.resources.IParagraph',
                'path': '...'
            }
        },
        {
            'code': ...,
            'body': ...
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

    >>> propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': batch_resp[0]['body']['path']})
    ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': batch_resp[1]['body']['path']})
    ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': 0})
    ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': 1})
    ... propv2_vrsbl = propv2['data']['adhocracy.sheets.versions.IVersionable']
    ... propv2_vrsbl['follows'] = [{'content_type': prop['content_type'], 'path': prop['path']}]
    ... batch = [ { 'method': 'POST',
    ...             'path': prop['postroot'],
    ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    ...           { 'method': 'POST',
    ...             'path': prop['postroot'],
    ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    ...                       'data': { 'adhocracy.sheets.document.Text': {
    ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    ...           { 'method': 'POST',
    ...             'path': propv2_vrsbl['postroot'],
    ...             'body': propv2 }
    ...         ]
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> pprint(batch_resp)
    [
        {
            'code': 200,
            'body': {
                'content_type': 'adhocracy.resources.IParagraph',
                'path': '...'
            }
        },
        {
            'code': 200,
            'body': {
                'content_type': 'adhocracy.resources.IParagraph',
                'path': '...'
            }
        },
        {
            'code': 200,
            'body': {
                'content_type': 'adhocracy.resources.proposal.IProposal',
                'path': '...'
            }
        }
    ]
    >>> propv3 = testapp.get_json(batch_resp[2]['body']['path']).json
    {
        'content_type': 'adhocracy.resources.proposal.IProposal',
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
