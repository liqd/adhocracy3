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

Terminology: we refer to content interfaces and the objects specified
by content interfaces as "resources"; resources consist of "sheets"
which are based on the substance-d concept of property sheet
interfaces.

Every Resource has multiple sheets that define schemata to set/get data.

There are 4 main types of resources:

* Pool: folder content in the object hierarchy, can contain other Pools
  (subfolders) and Items of any kind.
* Item (old name: FubelVersions-Pool): base class of any versionable items,
  such as Proposals, Documents, Sections etc. Contains a list of
  ItemVersions, sub-Items (e.g. Sections within Documents), and meta-data
  such as Tags.
* ItemVersion (old name: Versionable-Fubel): a specific version of a
  versionable item, e.g. a ProposalVersion, DocumentVersion, or
  SectionVersion.
* Simple: Base class of anything that is neither versionable nor a
  container (old name: any Fubel that is not a Versionable-Fubel).  For
  versionables, use Item instead; for non-versionable containers, use Pool
  instead.

A frequently used derived type is:

* Tag: a subtype of Simple, points to one (or sometimes zero or many)
  ItemVersion, e.g. the current HEAD or the last APPROVED version of a
  Document (old name: Tag-Fubel). Can be modified but doesn't have its own
  version history, hence it's a Simple instead of an Item.

Example resource hierarchy::

    Pool:         categories
    Simple:       categories/blue

    Pool:         proposals
    Item:         proposals/proposal1
    ItemVersion:  proposals/proposal1/v1
    Tag:          proposals/proposal1/head

    Item:         proposals/proposal1/section1
    ItemVersion:  proposals/proposal1/section1/v1
    Tag:          proposals/proposal1/section1/head


Meta-API
--------

The backend needs to answer to kinds of questions:

 1. Globally: What resources (content types) exist?  What sheets may or
    must they contain?  (What parts of) what sheets are
    read-only?  mandatory?  optional?

 2. In the context of a given session and URL: What HTTP methods are
    allowed?  With what resource objects in the body?  What are the
    authorizations (display / edit / vote-on / ...)?

The second kind is implemented with the OPTIONS method on the existing
URLs.  The first is implemented with the GET method on a dedicated URL.


Global Info
~~~~~~~~~~~

The dedicated prefix defaults to "/meta_api/", but can be customized. The
result is a JSON object with two main keys, "resources" and "sheets"::

    >>> resp_data = testapp.get("/meta_api/").json
    >>> sorted(resp_data.keys())
    ['resources', 'sheets']

The "resources" key points to an object whose keys are all the resources
(content types) defined by the system::

    >>> sorted(resp_data['resources'].keys())
    [...'adhocracy.resources.pool.IBasicPool', ...'adhocracy.resources.section.ISection'...]

Each of these keys points to an object describing the resource. If the
resource implements sheets (and a resource that doesn't would be
rather useless!), the object will have a "sheets" key whose value is a list
of the sheets implemented by the resource::

    >>> basicpool_desc = resp_data['resources']['adhocracy.resources.pool.IBasicPool']
    >>> sorted(basicpool_desc['sheets'])
    ['adhocracy.sheets.name.IName', 'adhocracy.sheets.pool.IPool'...]

If the resource is an item, it will also have a "item_type" key whose value
is the type of versions managed by this item (e.g. a Section will manage
SectionVersions as main element type)::

    >>> section_desc = resp_data['resources']['adhocracy.resources.section.ISection']
    >>> section_desc['item_type']
    'adhocracy.resources.section.ISectionVersion'

If the resource is a pool or item that can contain resources, it will also
have an "element_types" key whose value is the list of all resources the
pool/item can contain (including the "item_type" if it's an item). For
example, a pool can contain other pools; a section can contain tags. ::

    >>> basicpool_desc['element_types']
    ['adhocracy.interfaces.IPool'...]
    >>> sorted(section_desc['element_types'])
    ['adhocracy.interfaces.ITag', ...'adhocracy.resources.section.ISectionVersion'...]

The "sheets" key points to an object whose keys are all the sheets
implemented by any of the resources::

     >>> sorted(resp_data['sheets'].keys())
     [...'adhocracy.sheets.name.IName', ...'adhocracy.sheets.pool.IPool'...]

Each of these keys points to an object describing the resource. Each of
these objects has a "fields" key whose value is a list of objects
describing the fields defined by the sheet:

    >>> pprint(resp_data['sheets']['adhocracy.sheets.name.IName']['fields'][0])
    {'createmandatory': False,
     'name': 'name',
     'readonly': False,
     'valuetype': 'adhocracy.schema.Identifier'}

Each field definition has the following keys:

name
    The field name

createmandatory
    Flag specifying whether the field must be set if the sheet is created

readonly
    Flag specifying whether the field can be set by the user (if true, it's
    automatically set by the server)

valuetype
    The type of values stored in the field, either a basic type (as defined
    by Colander) such as "String" or "Integer", or a custom-defined type
    such as "adhocracy.schema.AbsolutePath"

There also is an optional key:

containertype
    Only present if the field can store multiple values (each of the type
    specified by the "valuetype" attribute). If present, the value of this
    attribute is either "list" (a list of values: order matters, duplicates
    are allowed) or "set" (a set of values: unordered, no duplicates).

For example, the 'subsections' field of ISection is an ordered list:

    >>> secfields = resp_data['sheets']['adhocracy.sheets.document.ISection']['fields']
    >>> for field in secfields:
    ...     if field['name'] == 'subsections':
    ...         pprint(field)
    ...         break
    {'containertype': 'list',
     'createmandatory': False,
     'name': 'subsections',
     'readonly': False,
     'valuetype': 'adhocracy.schema.AbsolutePath'}

The 'follows' field of IVersionable, however, is an unordered set:

    >>> verfields = resp_data['sheets']['adhocracy.sheets.versions.IVersionable']['fields']
    >>> for field in verfields:
    ...     if field['name'] == 'follows':
    ...         pprint(field)
    ...         break
    {'containertype': 'set',
     'createmandatory': False,
     'name': 'follows',
     'readonly': False,
     'valuetype': 'adhocracy.schema.AbsolutePath'}

OPTIONS
~~~~~~~

Returns possible methods for this resource, example request/response data
structures and available interfaces with resource data. The result is a
JSON object that has the allowed request methods as keys::

    >>> resp_data = testapp.options("/adhocracy").json
    >>> sorted(resp_data.keys())
    ['GET', 'HEAD', 'OPTION', 'POST', 'PUT']

If a GET, POST, or PUT request is allowed, the corresponding key will point
to an object that contains at least "request_body" and "response_body" as
keys::

    >>> sorted(resp_data['GET'].keys())
    [...'request_body', ...'response_body'...]
    >>> sorted(resp_data['POST'].keys())
    [...'request_body', ...'response_body'...]
    >>> sorted(resp_data['PUT'].keys())
    [...'request_body', ...'response_body'...]

The "response_body" sub-key returned for a GET request gives a stub view of
the actual response body that will be returned::

    >>> pprint(resp_data['GET']['response_body'])
    {'content_type': '',
     'data': {...'adhocracy.sheets.name.IName': {}...},
     'path': ''}

"content_type" and "path" will be filled in responses returned by an actual
GET request. "data" points to an object whose keys are the property sheets
that are part of the returned resource. The corresponding values will be
filled during actual GET requests; the stub contains just empty objects
("{}") instead.

If the current user has the right to post new versions of the resource or
add new details to it, the "request_body" sub-key returned for POST points
to a array of stub views of allowed requests::

    >>> data_post_pool = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...                   'data': {'adhocracy.sheets.name.IName': {}}}
    >>> data_post_pool in resp_data["POST"]["request_body"]
    True

The "response_body" sub-key again gives a stub view of the response
body::

     >>> pprint(resp_data['POST']['response_body'])
     {'content_type': '', 'path': ''}

If the current user has the right to modify the resource in-place, the
"request_body" sub-key returned for PUT gives a stub view of how the actual
request should look like::

     >>> pprint(resp_data['PUT']['request_body'])
     {'data': {...'adhocracy.sheets.name.IName': {}...}}

The "response_body" sub-key gives, as usual, a stub view of the resulting
response body::

     >>> pprint(resp_data['PUT']['response_body'])
     {'content_type': '', 'path': ''}


Basic calls
-----------

We can use the following http verbs to work with resources.


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

Returns resource and child elements meta data and all sheet with data::

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
sheets are central to version control in adhocracy: IDAG and
IVersion.  IVersion is in all resources that support version
control, and IDAG is a container that manages all versions of a
particular content element in a directed acyclic graph.

IDAGs as well as IVersions need to be created
explicitly by the frontend.

The server supports updating a resource that implements IVersion by
letting you post a content element with missing IVersion sheet
to the DAG (IVersion is read-only and managed by the server), and
passing a list of parent versions in the post parameters of the
request.  If there is only one parent version, the new version either
forks off an existing branch or just continues a linear history.  If
there are several parent versions, we have a merge commit.

Example: If a new versionable content element has been created by the
user, the front-end first posts an IDAG.  The IDAG works a little like
an IPool in that it allows posting versions to it.  The front-end will
then simply post the initial version into the IDAG with an empty
predecessor version list.

IDAGs may also implement the IPool sheet for
containing further IDAGs for sub-structures of
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

Create a Proposal (a subclass of Item which pools ProposalVersion's) ::

    >>> pdag = {'content_type': 'adhocracy.resources.proposal.IProposal',
    ...         'data': {
    ...              'adhocracy.sheets.name.IName': {
    ...                  'name': 'kommunismus'}
    ...              }
    ...         }
    >>> resp = testapp.post_json("/adhocracy/Proposals", pdag)
    >>> pdag_path = resp.json["path"]
    >>> pdag_path
    '/adhocracy/Proposals/kommunismus'

The return data has the new attribute 'first_version_path' to get the path first Version::

    >>> pvrs0_path = resp.json['first_version_path']  # FIXME: generalize over 'first_version_path'?
    >>> pvrs0_path
    '/adhocracy/Proposals/kommunismus/VERSION_0000000'

Version IDs are numeric and assigned by the server.  The front-end has
no control over them, and they are not supposed to be human-memorable.
For human-memorable version pointers that also allow for complex
update behavior (fixed-commit, always-newest, ...), consider
sheet ITags.

The Proposal has the IVersions and ITags interfaces to work with Versions::

    >>> resp = testapp.get(pdag_path)
    >>> resp.json['data']['adhocracy.sheets.versions.IVersions']['elements']
    ['/adhocracy/Proposals/kommunismus/VERSION_0000000']

    >>> resp.json['data']['adhocracy.sheets.tags.ITags']['elements']
    ['/adhocracy/Proposals/kommunismus/FIRST', '/adhocracy/Proposals/kommunismus/LAST']

Update
~~~~~~

Fetch the first Proposal Version, it is empty ::

    >>> resp = testapp.get(pvrs0_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.document.IDocument'])
    {'description': '', 'elements': [], 'title': ''}

    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersionable'])
    {'follows': []}

Create a new version of the proposal that follows the first version ::

    >>> pvrs = {'content_type': 'adhocracy.resources.proposal.IProposalVersion',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'title': 'kommunismus jetzt!',
    ...                     'description': 'blabla!',
    ...                     'elements': []},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [pvrs0_path]}  # FIXME: should be a reference ('{"content_type": ..., "path": ...}').  this issue occurs a few more times in this document.
    ...             }}
    >>> resp = testapp.post_json(pdag_path, pvrs)
    >>> pvrs1_path = resp.json["path"]
    >>> pvrs1_path != pvrs0_path
    True


Add and update child resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a Section item inside the Proposal item::

    >>> sdag = {'content_type': 'adhocracy.resources.section.ISection',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel1'},}
    ...         }
    >>> resp = testapp.post_json(pdag_path, sdag)
    >>> sdag_path = resp.json["path"]
    >>> svrs0_path = resp.json["first_version_path"]

Create a third Proposal version and add the first Section version ::

    >>> pvrs = {'content_type': 'adhocracy.resources.proposal.IProposalVersion',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'elements': [svrs0_path]},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [pvrs1_path],}
    ...                 }}
    >>> resp = testapp.post_json(pdag_path, pvrs)
    >>> pvrs2_path = resp.json["path"]

If we create a second Section version ::

    >>> vers = {'content_type': 'adhocracy.resources.section.ISectionVersion',
    ...         'data': {
    ...              'adhocracy.sheets.document.ISection': {
    ...                  'title': 'Kapitel Überschrift Bla',
    ...                  'elements': []},
    ...               'adhocracy.sheets.versions.IVersionable': {
    ...                  'follows': [svrs0_path],
    ...                  'root_version': [pvrs2_path]
    ...                  }   # the two lists in this dict must have the same length!
    ...          }}
    >>> resp = testapp.post_json(sdag_path, vers)
    >>> svrs1_path = resp.json['path']
    >>> svrs1_path != svrs0_path
    True

we automatically create a fourth Proposal version ::

    >>> resp = testapp.get(pdag_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersions'])
    {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000000',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000001',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000002',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000003']}

FIXME: the elements listing in the ITags interface is not very helpful, the
tag names (like 'FIRST') are missing.

FIXME: should we add a Tag TAG_LAST, to reference the last added version?

FIXME: should the server tell in general where to post speccific
content types? (like 'like', 'discussion',..)?  in other words,
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

    .. >>> batch = [ { 'method': 'POST',
    .. ...             'path': propv2['postroot'],
    .. ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'sein blick ist vom vorüberziehn der stäbchen' }}}},
    .. ...           { 'method': 'POST',
    .. ...             'path': propv2['postroot'],
    .. ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'ganz weiß geworden, so wie nicht mehr frisch' }}}},
    .. ...           { 'method': 'POST',
    .. ...             'path': propv2['postroot'],
    .. ...             'body': { 'content_type': 'this is not a very well-known content-type, and will trigger an error!',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    .. ...           { 'method': 'POST',
    .. ...             'path': propv2['postroot'],
    .. ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    .. >>> batch_resp = testapp.post_json(batch_url, batch).json
    .. >>> pprint(batch_resp)
    .. [
    ..     {
    ..         'code': 200,
    ..         'body': {
    ..             'content_type': 'adhocracy.resources.IParagraph',
    ..             'path': '...'
    ..         }
    ..     },
    ..     {
    ..         'code': 200,
    ..         'body': {
    ..             'content_type': 'adhocracy.resources.IParagraph',
    ..             'path': '...'
    ..         }
    ..     },
    ..     {
    ..         'code': ...,
    ..         'body': ...
    ..     }
    .. ]

(The third element of the above array must have return code >= 400.
Not sure how to test this with doctest.)

Do this again with the last two paragraphs, but without the mistake
above.  Also throw in a request at the end that depends on the former.
References to objects earlier in the same batch request are easy:
Instead of a string that contains the URI, the 'path' field of the
reference object contains a number that points into the batch array
(numbering starts with '0').  (Numeric paths are only allowed in batch
requests!)

    .. >>> propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    .. ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': batch_resp[0]['body']['path']})
    .. ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    .. ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': batch_resp[1]['body']['path']})
    .. ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    .. ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': 0})
    .. ... propv2['data']['adhocracy.sheets.document.IDocument']['paragraphs']
    .. ...      .append({ 'content_type': 'adhocracy.resources.IParagraph', 'path': 1})
    .. ... propv2_vrsbl = propv2['data']['adhocracy.sheets.versions.IVersionable']
    .. ... propv2_vrsbl['follows'] = [{'content_type': prop['content_type'], 'path': prop['path']}]
    .. ... batch = [ { 'method': 'POST',
    .. ...             'path': prop['postroot'],
    .. ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'ihm ist als ob es tausend stäbchen gäbchen' }}}},
    .. ...           { 'method': 'POST',
    .. ...             'path': prop['postroot'],
    .. ...             'body': { 'content_type': 'adhocracy.resources.IParagraph',
    .. ...                       'data': { 'adhocracy.sheets.document.Text': {
    .. ...                           'text': 'und in den tausend stäbchen keinen fisch' }}}},
    .. ...           { 'method': 'POST',
    .. ...             'path': propv2_vrsbl['postroot'],
    .. ...             'body': propv2 }
    .. ...         ]
    .. >>> batch_resp = testapp.post_json(batch_url, batch).json
    .. >>> pprint(batch_resp)
    .. [
    ..     {
    ..         'code': 200,
    ..         'body': {
    ..             'content_type': 'adhocracy.resources.IParagraph',
    ..             'path': '...'
    ..         }
    ..     },
    ..     {
    ..         'code': 200,
    ..         'body': {
    ..             'content_type': 'adhocracy.resources.IParagraph',
    ..             'path': '...'
    ..         }
    ..     },
    ..     {
    ..         'code': 200,
    ..         'body': {
    ..             'content_type': 'adhocracy.resources.proposal.IProposal',
    ..             'path': '...'
    ..         }
    ..     }
    .. ]
    .. >>> propv3 = testapp.get_json(batch_resp[2]['body']['path']).json
    .. {
    ..     'content_type': 'adhocracy.resources.proposal.IProposal',
    ..     ...
    .. }


Other stuff
-----------

GET /interfaces/..::

    Get schema/interface information: attribute type/required/readonly, ...
    Get interface inheritage


GET/POST /workflows/..::

    Get workflow, apply workflow to resource.


GET/POST /transitions/..::

    Get available workflow transitions for resource, execute transition.


GET /query/..::

    query catalog to find content below /instances/spd


GET/POST /users::

    Get/Add user
