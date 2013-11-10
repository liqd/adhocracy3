Adhocracy 3 loosed coupling REST-API with substance-d backend
=============================================================

Prerequisites
-------------

usefull imports to work with rest api calls  ::

    >>> import requests
    >>> from pprint import pprint

start adhocracy testapp ::

    >>> from webtest import TestApp
    >>> from adhocracy.testing import config
    >>> from adhocracy import main
    >>> app = main({}, **config)
    Executing evolution step ...
    >>> testapp = TestApp(app)


Basic calls, working with Pool content
--------------------------------------

OPTIONS
~~~~~~~

Returns possible methods for this resource and available interfaces
with resources data::

    >>> resp = testapp.options("/adhocracy")
    >>> pprint(resp.json)
    {'GET': ['adhocracy.interfaces.IName'],
     'HEAD': [],
     'POST': ['adhocracy.interfaces.INodeContainer',
              'adhocracy.interfaces.IParagraphContainer',
              'adhocracy.interfaces.IPool',
              'adhocracy.interfaces.IProposalContainer'],
     'PUT': ['adhocracy.interfaces.IName']}

HEAD
~~~~

Returns only http headers for this resource::

    >>> resp = testapp.head("/adhocracy")
    >>> resp.headerlist # doctest: +ELLIPSIS
    [('Content-Type', 'application/json; charset=UTF-8'), ...
    >>> resp.text
    ''

GET
~~~~

Returns resource meta data, children meta data and all interfaces with data::

    >>> resp = testapp.get("/adhocracy", )
    >>> pprint(resp.json)
    {'children': [],
     'content_type': 'adhocracy.interfaces.IPool',
     'data': {'adhocracy.interfaces.IName': {'name': ''}},
     'meta': {'content_type': 'adhocracy.interfaces.IPool',
              'content_type_name': 'adhocracy.interfaces.IPool',
              'creation_date': '',
              'creator': '',
              'name': 'adhocracy',
              'oid': ...
              'path': '/adhocracy',
              'workflow_state': ''}}


PUT
~~~~

Modify and return the path of the modified resource::

    >>> data = {'content_type': 'adhocracy.interfaces.IPool',
    ...         'data': {'adhocracy.interfaces.IName': {'name': 'NEWTITLE'}}}
    >>> resp = testapp.put_json("/adhocracy", data)
    >>> resp.json
    {'path': '/adhocracy'}


FIXME: write test cases for "any sub-structure of an object in a PUT
request may be missing and will be replaced by the old (overwritten)
sub-structure.

FIXME: write test cases for attributes with "required", "read-only",
and possibly others.  (those work the same in PUT and POST, and on any
attribute in the json tree.)


POST
~~~~

Create new resource and return the path::

    >>> prop = {'content_type': 'adhocracy.contents.interfaces.IProposal',
    ...         'data': {
    ...              'adhocracy.propertysheets.interfaces.IName': {
    ...                  'name': 'kommunismus jetzt!'},
    ...              'adhocracy.propertysheets.interfaces.IDocument': {
    ...                  'title': 'kommunismus jetzt!',
    ...                  'description': 'blabla!',
    ...                  'paragraphs': []}}}
    >>> resp = testapp.post_json("/adhocracy", prop)
    >>> pprint_json(resp.json)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "path": "/adhocracy/...
    }

Fetch posted initial version and extract URL for POSTing updates:

    >>> resp = testapp.get_json(resp.json["path"])
    >>> prop = resp.json
    >>> pprint_json(prop)
    {
        "content_type": "adhocracy.contents.interfaces.IProposal",
        "data": ...
        "path": "/adhocracy/...
        "postroot": "/adhocracy/...
    }

FIXME: find technical term for things that have "post_path" and live
in "postroots"(?) and for things that initiate "postroots"(?) in
particular.  (paragraphs have a "post_path", but they live with
proposals and such.)

FIXME: should "post_path" live in a property sheet, or on top level in
the content object?

Create new paragraph and add it to proposal:

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
        "path": "/adhocracy/...
    }
    >>> resp = testapp.get_json(resp.json["path"])
    >>> para = resp.json
    >>> prop["data"]["adhocracy.propertysheets.interfaces.IDocument"]["paragraphs"]
    ...      .append(para["path"])

Update versionable predecessor version and get dag-postroot:

(FIXME: s/follows/predecessors/g; s/followed_by/successors/g;?)

    >>> prop_vrsbl = prop["data"]["adhocracy.propertysheets.interfaces.IVersionable"]
    >>> prop_vrsbl["follows"] = [para["path"]]
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

FIXME: write test cases for "any sub-structure of an object in a POST
request may be missing and will be replaced by defaults."

(Note: the server may handle paths like the following internally, but
the client is not supposed to worry about that:
  proposalspool/ => proposalspool/proposal1/dag/prosoal1V1
  proposalspool/proposal1/ => proposalspool/proposal1/absatz1pool/dag/absatz1V1)







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

The new PropsalContainer has a child _versions to store all proposal node versions ::

    >>> resp = testapp.get("/adhocracy/proposal1/_versions")
    >>> children = resp.json["children"]
    >>> len(children)
    1

The initial node without follow Nodes is already there ::

    >>> proposalv1 = children[0]
    >>> resp = testapp.get(proposalv1["path"])
    >>> pprint(resp.json["data"])
    {'adhocracy.interfaces.IDocument': {'description': '',
                                        'paragraphs': [],
                                        'title': ''},
     'adhocracy.interfaces.IVersionable': {'follows': []}}



If we change this node we create a new version, so we have to mind
the right follows relation ::

    >>> data =  {'content_type': 'adhocracy.interfaces.IProposal',
    ...          'data': {'adhocracy.interfaces.IDocument': {'description': 'synopsis', 'title': 'title'},
    ...                   'adhocracy.interfaces.IVersionable': {'follows': [proposalv1["path"]]}}}
    >>> resp = testapp.put_json(proposalv1["path"], data)
    >>> resp.json
    {'path': '/adhocracy/proposal1/_versions/...

    >>> proposalv2 = resp.json
    >>> proposalv2['path'] != proposalv1["path"]
    True

NOTE: PUT for INode content is not idempotent, this breaks the REST architecture principles


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

