# doctest: +ELLIPSIS
# doctest: +NORMALIZE_WHITESPACE

REST-API (with loose coupling)
==============================

Prerequisites
-------------

Some imports to work with rest api calls::

    >>> import copy
    >>> from functools import reduce
    >>> from operator import itemgetter
    >>> import os
    >>> import requests
    >>> from pprint import pprint

Start Adhocracy testapp::

    >>> from webtest import TestApp
    >>> app = getfixture('app_sample')
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
    [...'adhocracy.resources.pool.IBasicPool', ...'adhocracy_sample.resources.section.ISection'...]

Each of these keys points to an object describing the resource. If the
resource implements sheets (and a resource that doesn't would be
rather useless!), the object will have a "sheets" key whose value is a list
of the sheets implemented by the resource::

    >>> basicpool_desc = resp_data['resources']['adhocracy.resources.pool.IBasicPool']
    >>> sorted(basicpool_desc['sheets'])
    ['adhocracy.sheets.metadata.IMetadata', 'adhocracy.sheets.name.IName', 'adhocracy.sheets.pool.IPool'...]

If the resource is an item, it will also have a "item_type" key whose value
is the type of versions managed by this item (e.g. a Section will manage
SectionVersions as main element type)::

    >>> section_desc = resp_data['resources']['adhocracy_sample.resources.section.ISection']
    >>> section_desc['item_type']
    'adhocracy_sample.resources.section.ISectionVersion'

If the resource is a pool or item that can contain resources, it will also
have an "element_types" key whose value is the list of all resources the
pool/item can contain (including the "item_type" if it's an item). For
example, a pool can contain other pools; a section can contain tags. ::

    >>> basicpool_desc['element_types']
    ['adhocracy.interfaces.IPool'...]
    >>> sorted(section_desc['element_types'])
    ['adhocracy.interfaces.ITag', ...'adhocracy_sample.resources.section.ISectionVersion'...]

The "sheets" key points to an object whose keys are all the sheets
implemented by any of the resources::

     >>> sorted(resp_data['sheets'].keys())
     [...'adhocracy.sheets.name.IName', ...'adhocracy.sheets.pool.IPool'...]

Each of these keys points to an object describing the resource. Each of
these objects has a "fields" key whose value is a list of objects
describing the fields defined by the sheet:

    >>> pprint(resp_data['sheets']['adhocracy.sheets.name.IName']['fields'][0])
    {'creatable': True,
     'create_mandatory': True,
     'editable': False,
     'name': 'name',
     'readable': True,
     'valuetype': 'adhocracy.schema.Name'}

Each field definition has the following keys:

name
    The field name

create_mandatory
    Flag specifying whether the field must be set if the sheet is created
    (post requests).

readable
    Flag specifying whether the field can be read (get requests).

editable
    Flag specifying whether the field can be set to edit an existing sheet
    (put requests).

creatable
    Flag specifying whether the field can be set if the sheet is created
    (post requests).

valuetype
    The type of values stored in the field, either a basic type (as defined
    by Colander) such as "String" or "Integer", or a custom-defined type
    such as "adhocracy.schema.AbsolutePath"

There also are some optional keys:

containertype
    Only present if the field can store multiple values (each of the type
    specified by the "valuetype" attribute). If present, the value of this
    attribute is either "list" (a list of values: order matters, duplicates
    are allowed) or "set" (a set of values: unordered, no duplicates).

targetsheet
    Only present if "valuetype" is a path
    ("adhocracy.schema.AbsolutePath"). If present, it gives the name of the
    sheet that all pointed-to resources will implement (they might possibly
    be of different types, but they will always implement the given sheet
    or they wouldn't be valid link targets).

For example, the 'subsections' field of ISection is an ordered list
pointing to other ISection's:

    >>> secfields = resp_data['sheets']['adhocracy.sheets.document.ISection']['fields']
    >>> for field in secfields:
    ...     if field['name'] == 'subsections':
    ...         pprint(field)
    ...         break
    {'containertype': 'list',
     'creatable': True,
     'create_mandatory': False,
     'editable': True,
     'name': 'subsections',
     'readable': True,
     'targetsheet': 'adhocracy.sheets.document.ISection',
     'valuetype': 'adhocracy.schema.AbsolutePath'}

The 'follows' field of IVersionable is an unordered set pointing to other
IVersionable's:

...    >>> verfields = resp_data['sheets']['adhocracy.sheets.versions.IVersionable']['fields']
...    >>> for field in verfields:
...    ...     if field['name'] == 'follows':
...    ...         pprint(field)
...    ...         break
...    {'containertype': 'set',
...     'creatable': True,
...     'create_mandatory': False,
...     'name': 'follows',
...     'editable': True,
...     'readable': True,
...     'targetsheet': 'adhocracy.sheets.versions.IVersionable',
...     'valuetype': 'adhocracy.schema.AbsolutePath'}

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

...     >>> pprint(resp_data['PUT']['request_body'])
...     {'data': {...'adhocracy.sheets.name.IName': {}...}}

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
    {'adhocracy.sheets.metadata.IMetadata': ...
     'adhocracy.sheets.name.IName': {'name': 'adhocracy'},
     'adhocracy.sheets.pool.IPool': {'elements': [...]}}

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

    FIXME: disable because IName.name is not editable.  use another example!

...    >>> data = {'content_type': 'adhocracy.resources.pool.IBasicPool',
...    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'youdidntexpectthis'}}}
...    >>> resp_data = testapp.put_json("/adhocracy/Proposals", data).json
...    >>> pprint(resp_data)
...    {'content_type': 'adhocracy.resources.pool.IBasicPool',
...     'path': '/adhocracy/Proposals'}

Check the changed resource ::

...   >>> resp_data = testapp.get("/adhocracy/Proposals").json
...   >>> resp_data["data"]["adhocracy.sheets.name.IName"]["name"]
...   'youdidntexpectthis'

FIXME: write test cases for attributes with "create_mandatory",
"editable", etc.  (those work the same in PUT and POST, and on any
attribute in the json tree.)


ERROR Handling
~~~~~~~~~~~~~~

FIXME: ... is not working anymore in this doctest

The normal return code is 200 ::

    >>> data = {'content_type': 'adhocracy.resources.pool.IBasicPool',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'Proposals'}}}

.. >>> testapp.put_json("/adhocracy/Proposals", data)
.. 200 OK application/json ...

If you submit invalid data the return error code is 400 ::

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

    >>> pdag = {'content_type': 'adhocracy_sample.resources.proposal.IProposal',
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

    >>> pvrs0_path = resp.json['first_version_path']
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

Fetch the first Proposal version, it is empty ::

    >>> resp = testapp.get(pvrs0_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.document.IDocument'])
    {'description': '', 'elements': [], 'title': ''}

    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersionable'])
    {'followed_by': [], 'follows': []}

Create a new version of the proposal that follows the first version ::

    >>> pvrs = {'content_type': 'adhocracy_sample.resources.proposal.IProposalVersion',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'title': 'kommunismus jetzt!',
    ...                     'description': 'blabla!',
    ...                     'elements': []},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [pvrs0_path]}},
    ...          'root_versions': [pvrs0_path]}
    >>> resp = testapp.post_json(pdag_path, pvrs)
    >>> pvrs1_path = resp.json["path"]
    >>> pvrs1_path != pvrs0_path
    True


Add and update child resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We expect certain Versionable fields for the rest of this test suite
to work ::

    >>> resp = testapp.get('/meta_api')
    >>> vers_fields = resp.json['sheets']['adhocracy.sheets.versions.IVersionable']['fields']
    >>> pprint(sorted(vers_fields, key=itemgetter('name')))
    [{'containertype': 'list',
      'creatable': False,
      'create_mandatory': False,
      'editable': False,
      'name': 'followed_by',
      'readable': True,
      'targetsheet': 'adhocracy.sheets.versions.IVersionable',
      'valuetype': 'adhocracy.schema.AbsolutePath'},
     {'containertype': 'list',
      'creatable': True,
      'create_mandatory': False,
      'editable': True,
      'name': 'follows',
      'readable': True,
      'targetsheet': 'adhocracy.sheets.versions.IVersionable',
      'valuetype': 'adhocracy.schema.AbsolutePath'}]

The 'follows' element must be set by the client when it creates a new
version that is the successor of one or several earlier versions. The
'followed_by' element is automatically populated by the server by
"reversing" any 'follows' links pointing to the version in question.
Therefore 'followed_by' is read-only, while 'follows' is writable.

Create a Section item inside the Proposal item ::

    >>> sdag = {'content_type': 'adhocracy_sample.resources.section.ISection',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel1'},}
    ...         }
    >>> resp = testapp.post_json(pdag_path, sdag)
    >>> sdag_path = resp.json["path"]
    >>> svrs0_path = resp.json["first_version_path"]

and a second Section ::

    >>> sdag = {'content_type': 'adhocracy_sample.resources.section.ISection',
    ...         'data': {'adhocracy.sheets.name.IName': {'name': 'kapitel2'},}
    ...         }
    >>> resp = testapp.post_json(pdag_path, sdag)
    >>> s2dag_path = resp.json["path"]
    >>> s2vrs0_path = resp.json["first_version_path"]

Create a third Proposal version and add the two Sections in their
initial versions ::

    >>> pvrs = {'content_type': 'adhocracy_sample.resources.proposal.IProposalVersion',
    ...         'data': {'adhocracy.sheets.document.IDocument': {
    ...                     'elements': [svrs0_path, s2vrs0_path]},
    ...                  'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [pvrs1_path],}
    ...                 },
    ...          'root_versions': [pvrs1_path]}
    >>> resp = testapp.post_json(pdag_path, pvrs)
    >>> pvrs2_path = resp.json["path"]

If we create a second version of kapitel1 ::

    >>> svrs = {'content_type': 'adhocracy_sample.resources.section.ISectionVersion',
    ...         'data': {
    ...              'adhocracy.sheets.document.ISection': {
    ...                  'title': 'Kapitel Überschrift Bla',
    ...                  'elements': []},
    ...               'adhocracy.sheets.versions.IVersionable': {
    ...                  'follows': [svrs0_path]
    ...                  }
    ...          },
    ...          'root_versions': [pvrs2_path]
    ...         }
    >>> resp = testapp.post_json(sdag_path, svrs)
    >>> svrs1_path = resp.json['path']
    >>> svrs1_path != svrs0_path
    True

Whenever a IVersionable contains 'follows' link(s) to preceding versions,
there should be a top-level 'root_versions' element listing the version of
their root elements. 'root_versions' is a set, which means that order
doesn't matter and duplicates are ignored. In this case, it points to the
proposal version containing the section to update.

The 'root_versions' set allows automatical updates of items that embedding
or otherwise linking to the updated item. In this case, a fourth Proposal
version is automatically created along with the updated Section version::

    >>> resp = testapp.get(pdag_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersions'])
    {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000000',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000001',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000002',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000003']}

    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/VERSION_0000003')
    >>> pvrs3_path = resp.json['path']

More interestingly, if we then create a second version of kapitel2::

    >>> svrs = {'content_type': 'adhocracy_sample.resources.section.ISectionVersion',
    ...         'data': {
    ...              'adhocracy.sheets.document.ISection': {
    ...                  'title': 'on the hardness of version control',
    ...                  'elements': []},
    ...               'adhocracy.sheets.versions.IVersionable': {
    ...                  'follows': [s2vrs0_path]
    ...                  }
    ...          },
    ...          'root_versions': [pvrs3_path]
    ...         }
    >>> resp = testapp.post_json(s2dag_path, svrs)
    >>> s2vrs1_path = resp.json['path']
    >>> s2vrs1_path != s2vrs0_path
    True

a Proposal version is automatically created only for pvrs3, not for
pvrs2 (which also contains s2vrs0_path) ::

    >>> resp = testapp.get(pdag_path)
    >>> pprint(resp.json['data']['adhocracy.sheets.versions.IVersions'])
    {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000000',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000001',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000002',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000003',
                  '/adhocracy/Proposals/kommunismus/VERSION_0000004']}

    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/VERSION_0000004')
    >>> pvrs4_path = resp.json['path']
    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/VERSION_0000002')
    >>> len(resp.json['data']['adhocracy.sheets.versions.IVersionable']['followed_by'])
    1

    >>> len(resp.json['data']['adhocracy.sheets.versions.IVersionable']['followed_by'])
    1

    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/VERSION_0000004')
    >>> len(resp.json['data']['adhocracy.sheets.versions.IVersionable']['followed_by'])
    0

FIXME: If two frontends post competing sections simultaneously,
neither knows which proposal version belongs to whom.  Proposed
solution: the post response must tell the frontend the changed
``root_version``.


Tags
~~~~

Each Versionable has a FIRST tag that points to the initial version::

    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/FIRST')
    >>> pprint(resp.json)
    {'content_type': 'adhocracy.interfaces.ITag',
     'data': {...
              'adhocracy.sheets.name.IName': {'name': 'FIRST'},
              'adhocracy.sheets.tags.ITag': {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000000']}},
     'path': '/adhocracy/Proposals/kommunismus/FIRST'}

It also has a LAST tag that points to the newest versions -- any versions
that aren't 'followed_by' any later version::

    >>> resp = testapp.get('/adhocracy/Proposals/kommunismus/LAST')
    >>> pprint(resp.json)
    {'content_type': 'adhocracy.interfaces.ITag',
     'data': {...
              'adhocracy.sheets.name.IName': {'name': 'LAST'},
              'adhocracy.sheets.tags.ITag': {'elements': ['/adhocracy/Proposals/kommunismus/VERSION_0000004']}},
     'path': '/adhocracy/Proposals/kommunismus/LAST'}

FIXME: the elements listing in the ITags interface is not very helpful, the
tag names (like 'FIRST') are missing.

FIXME: should the server tell in general where to post specific
content types? (like 'like', 'discussion',..)?  in other words,
should the client be able to ask (e.g. with an OPTIONS request)
where to post a 'like'?


Comments
--------

To give another example of a versionable content type, we can write comments
about proposals::

    >>> comment = {'content_type': 'adhocracy_sample.resources.comment.IComment',
    ...            'data': {}}
    >>> resp = testapp.post_json(pdag_path, comment)
    >>> comment_path = resp.json["path"]
    >>> comment_path
    '/adhocracy/Proposals/kommunismus/comment_000...'
    >>> first_commvers_path = resp.json['first_version_path']
    >>> first_commvers_path
    '/adhocracy/Proposals/kommunismus/comment_000.../VERSION_0000000'

The first comment version is empty (as with all versionables), so lets add
another version to say something meaningful. A comment contains *content*
(arbitrary text) and *refers_to* a specific version of a proposal. ::

    >>> commvers = {'content_type': 'adhocracy_sample.resources.comment.ICommentVersion',
    ...             'data': {
    ...                 'adhocracy_sample.sheets.comment.IComment': {
    ...                     'refers_to': pvrs4_path,
    ...                     'content': 'Gefällt mir, toller Vorschlag!'},
    ...                 'adhocracy.sheets.versions.IVersionable': {
    ...                     'follows': [first_commvers_path]}},
    ...             'root_versions': [first_commvers_path]}
    >>> resp = testapp.post_json(comment_path, commvers)
    >>> snd_commvers_path = resp.json['path']
    >>> snd_commvers_path
    '/adhocracy/Proposals/kommunismus/comment_000.../VERSION_0000001'

Comments can be about any versionable that allows posting comments. Hence
it's also possible to write a comment about another comment::

    >>> metacomment = {'content_type': 'adhocracy_sample.resources.comment.IComment',
    ...                 'data': {}}
    >>> resp = testapp.post_json(pdag_path, metacomment)
    >>> metacomment_path = resp.json["path"]
    >>> metacomment_path
    '/adhocracy/Proposals/kommunismus/comment_000...'
    >>> comment_path != metacomment_path
    True
    >>> first_metacommvers_path = resp.json['first_version_path']
    >>> first_metacommvers_path
    '/adhocracy/Proposals/kommunismus/comment_000.../VERSION_0000000'

As usual, we have to add another version to actually say something::

    >>> metacommvers = {'content_type': 'adhocracy_sample.resources.comment.ICommentVersion',
    ...                 'data': {
    ...                     'adhocracy_sample.sheets.comment.IComment': {
    ...                         'refers_to': snd_commvers_path,
    ...                         'content': 'Find ich nicht!'},
    ...                     'adhocracy.sheets.versions.IVersionable': {
    ...                         'follows': [first_metacommvers_path]}},
    ...                 'root_versions': [first_metacommvers_path]}
    >>> resp = testapp.post_json(metacomment_path, metacommvers)
    >>> snd_metacommvers_path = resp.json['path']
    >>> snd_metacommvers_path
    '/adhocracy/Proposals/kommunismus/comment_000.../VERSION_0000001'


Lets view all the comments referring to the proposal.
First find the path of the newest version of the proposal::

    >>> resp = testapp.get(pdag_path + '/LAST')
    >>> newest_prop_vers = resp.json['data']['adhocracy.sheets.tags.ITag']['elements'][-1]

Now we can retrieve that version and consult the 'comments' fields of its
'adhocracy_sample.sheets.comment.ICommentable' sheet::

    >>> resp = testapp.get(newest_prop_vers)
    >>> comlist = resp.json['data']['adhocracy_sample.sheets.comment.ICommentable']['comments']
    >>> comlist == [snd_commvers_path]
    True

Any commentable resource has this sheet. Since comments can refer to other
comments, they have it as well. Lets find out which other comments refer to
this comment version::

    >>> resp = testapp.get(snd_commvers_path)
    >>> comlist = resp.json['data']['adhocracy_sample.sheets.comment.ICommentable']['comments']
    >>> comlist == [snd_metacommvers_path]
    True


Batch requests
--------------

The following URL accepts batch requests ::

    >>> batch_url = '/batch'

A batch request a POST request with a json array in the body that
contains certain HTTP requests encoded in a certain way.

A success response contains in its body an array of encoded HTTP
responses.  This way, the client can see what happened to the
individual POSTS, and collect all the paths of the individual
resources that were posted.

Batch requests are processed as a transaction.  By this, we mean that
either all encoded HTTP requests succeed and the response to the batch
request is a success response, or any one of them fails, the database
state is rolled back to the beginning of the request, and the response
is an error, explaining which request failed for which reason.


Things that are different in individual requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Preliminary resource paths: motivation and general idea.*

All requests with methods POST, GET, PUT as allowed in the rest of
this document are allowed in batch requests.  POST differs in that it
yields *preliminary resource paths*.  To understand what that is,
consider this example: In step 4 of a batch request, the front-end
wants to post to the path that resulted from posting the parent
resource in step 3 of the same request, so batch requests need to
allow for an abstraction over the resource paths resulting from POST
requests.  POST yields preliminary paths instead of actual ones, and
POST, GET, and PUT are all allowed to use preliminary paths in
addition to the "normal" ones.  Apart from this, nothing changes in
the individual requests.

*Preliminary resource paths: implementation.*

The encoding of a request consist of an object with attributes for
method (aka HTTP verb), path, and body. A further attribute, 'result_path',
defines a name for the preliminary path of the object created by the request.
Like other resource names, the preliminary name is an *Identifier*,
i.e. it can only contain ASCII letters and digits, underscores, dashes,
and dots. In addition it must start with '@'. If the preliminary name will not be used, this attribute can be
omitted or left empty. ::

    >>> encoded_request_with_name = {
    ...     'method': 'POST',
    ...     'path': '/adhocracy/Proposal/kommunismus',
    ...     'body': { 'content_type': 'adhocracy_sample.resources.paragraph.IParagraph' },
    ...     'result_path': '@par1_item',
    ...     'result_first_version_path': '@par1_item/v1'
    ... }

Preliminary paths can be used anywhere in subsequent requests, either
in the 'path' item of the request itself, or anywhere in the json data
in the body where the schemas expect to find resource paths.  It must
be prefixed with "@" in order to mark it as preliminary.  Right
before executing the request, the backend will traverse the request
object and replace all preliminary names with the actual ones that
will be available by then.

At this point, the fact that an item is not constructed empty, but
always immediately contains an initial, empty version that is passed
back to the client via an extra attribute 'first_version_path'
complicates things significantly.

In order to post the first *real* item version, we must use
'first_version_path' as the predecessor version, but we can't know its
value before the post of the item version. This would not be a
problem if the item would be created empty.

*FIXME: change the api accordingly so that this problem goes away!*

In order to work around you can set the optional field
'result_first_version_path' with a *preliminary resource path*.


Examples
~~~~~~~~

Let's add some more paragraphs to the second section above ::

    >>> section_item = s2dag_path
    >>> batch = [ {
    ...             'method': 'POST',
    ...             'path': pdag_path,
    ...             'body': {
    ...                 'content_type': 'adhocracy_sample.resources.paragraph.IParagraph',
    ...                 'data': {'adhocracy.sheets.name.IName':
    ...                              {'name': 'par1'}
    ...                         }
    ...             },
    ...             'result_path': '@par1_item',
    ...             'result_first_version_path': '@par1_item/v1'
    ...           },
    ...           {
    ...             'method': 'POST',
    ...             'path': '@par1_item',
    ...             'body': {
    ...                 'content_type': 'adhocracy_sample.resources.paragraph.IParagraphVersion',
    ...                 'data': {
    ...                     'adhocracy.sheets.versions.IVersionable': {
    ...                         'follows': ['@par1_item/v1']
    ...                     },
    ...                     'adhocracy.sheets.document.IParagraph': {
    ...                         'content': 'sein blick ist vom vorüberziehn der stäbchen'
    ...                     }
    ...                 },
    ...             },
    ...             'result_path': '@par1_item/v2'
    ...           },
    ...           {
    ...             'method': 'GET',
    ...             'path': '@par1_item/v2'
    ...           },
    ...         ]
    >>> batch_resp = testapp.post_json(batch_url, batch).json
    >>> len(batch_resp)
    3
    >>> pprint(batch_resp[0])
    {'body': {'content_type': 'adhocracy_sample.resources.paragraph.IParagraph',
              'first_version_path': '/adhocracy/Proposals/kommunismus/par1/VERSION_0000000',
              'path': '/adhocracy/Proposals/kommunismus/par1'},
     'code': 200}
    >>> pprint(batch_resp[1])
    {'body': {'content_type': 'adhocracy_sample.resources.paragraph.IParagraphVersion',
              'path': '/adhocracy/Proposals/kommunismus/par1/VERSION_0000001'},
     'code': 200}
    >>> pprint(batch_resp[2])
    {'body': {'content_type': 'adhocracy_sample.resources.paragraph.IParagraphVersion',
              'data': {...},
              'path': '/adhocracy/Proposals/kommunismus/par1/VERSION_0000001'},
     'code': 200}
     >>> batch_resp[2]['body']['data']['adhocracy.sheets.document.IParagraph']['content']
     'sein blick ist vom vorüberziehn der stäbchen'


Now the first, empty paragraph version should contain the newly
created paragraph version as its only successor ::

    .. >>> v1 = batch_resp[2]['body']['data']['adhocracy.sheets.versions.IVersionable']['followed_by']
    .. >>> v2 = [batch_resp[1]['path']]
    .. >>> v1 == v2
    .. True
    .. >>> print(v1, v2)
    .. ...

The LAST tag should point to the version we created within the batch request::

    >>> resp_data = testapp.get("/adhocracy/Proposals/kommunismus/par1/LAST").json
    >>> resp_data['data']['adhocracy.sheets.tags.ITag']['elements']
    ['/adhocracy/Proposals/kommunismus/par1/VERSION_0000001']

Post another paragraph item and a version.  If the version post fails,
the paragraph will not be present in the database ::

    >>> invalid_batch = [ {
    ...             'method': 'POST',
    ...             'path': pdag_path,
    ...             'body': {
    ...                 'content_type': 'adhocracy_sample.resources.paragraph.IParagraph',
    ...                 'data': {'adhocracy.sheets.name.IName':
    ...                              {'name': 'par2'}
    ...                         }
    ...             },
    ...             'result_path': '@par2_item'
    ...           },
    ...           {
    ...             'method': 'POST',
    ...             'path': '@par2_item',
    ...             'body': {
    ...                 'content_type': 'NOT_A_CONTENT_TYPE_AT_ALL',
    ...                 'data': {
    ...                     'adhocracy.sheets.versions.IVersionable': {
    ...                         'follows': ['@par2_item/v1']
    ...                     },
    ...                     'adhocracy.sheets.document.IParagraph': {
    ...                         'content': 'das wird eh nich gepostet'
    ...                     }
    ...                 }
    ...             },
    ...             'result_path': '@par2_item/v2'
    ...           }
    ...         ]
    >>> invalid_batch_resp = testapp.post_json(batch_url, invalid_batch,
    ...                                        status=400).json
    >>> pprint(invalid_batch_resp)
    [{'body': {'content_type': 'adhocracy_sample.resources.paragraph.IParagraph',
               'first_version_path': '...',
               'path': '...'},
      'code': 200},
     {'body': {'errors': [...],
               'status': 'error'},
      'code': 400}]
    >>> get_nonexistent_obj = testapp.get(invalid_batch_resp[0]['body']['path'], status=404)
    >>> get_nonexistent_obj.status
    '404 Not Found'

Note that the response will contain embedded responses for all successful
encoded requests (if any) and also for the first failed encoded request (if
any), but not for any further failed requests. The backend stops processing
encoded requests once the first of them has failed, since further processing
would probably only lead to further errors.

FIXME: I don't think the tests are supposed to work as is, but they
should be clear enough to serve as documentation.  Fix this once the
application code that it is testing is supposed to work?  --mf

FIXME: The response does not have to have this particular type.  I
would prefer it if I could get the individual request responses (even
if they are obsolete), but in which syntax I don't care.  --mf


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
