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
    {'GET': ['adhocracy.propertysheets.interfaces.IName'],
     'HEAD': [],
     'POST': ['adhocracy.contents.interfaces.INodeContainer',
              'adhocracy.contents.interfaces.IParagraphContainer',
              'adhocracy.contents.interfaces.IPool',
              'adhocracy.contents.interfaces.IProposalContainer'],
     'PUT': ['adhocracy.propertysheets.interfaces.IName']}

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
     'content_type': 'adhocracy.contents.interfaces.IPool',
     'data': {'adhocracy.propertysheets.interfaces.IName': {'name': ''}},
     'meta': {'content_type': 'adhocracy.contents.interfaces.IPool',
              'content_type_name': 'adhocracy.contents.interfaces.IPool',
              'creation_date': '',
              'creator': '',
              'name': 'adhocracy',
              'oid': ...
              'path': '/adhocracy',
              'workflow_state': ''}}


PUT
~~~~

Modify and return the path of the modified resource::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IPool',
    ...         'data': {'adhocracy.propertysheets.interfaces.IName': {'name': 'NEWTITLE'}}}
    >>> resp = testapp.put_json("/adhocracy", data)
    >>> resp.json
    {'path': '/adhocracy'}


POST
~~~~

Create new resource and return the path::

    >>> data = {'content_type': 'adhocracy.contents.interfaces.IProposalContainer',
    ...         'data': {'adhocracy.propertysheets.interfaces.IName': {'name': 'proposal1'}}}
    >>> resp = testapp.post_json("/adhocracy", data)
    >>> resp.json
    {'path': '/adhocracy/proposal1'}


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
    {'adhocracy.propertysheets.interfaces.IDocument': {'description': '',
                                        'paragraphs': [],
                                        'title': ''},
     'adhocracy.propertysheets.interfaces.IVersionable': {'follows': []}}



If we change this node we create a new version, so we have to mind
the right follows relation ::

    >>> data =  {'content_type': 'adhocracy.contents.interfaces.IProposal',
    ...          'data': {'adhocracy.propertysheets.interfaces.IDocument': {'description': 'synopsis', 'title': 'title'},
    ...                   'adhocracy.propertysheets.interfaces.IVersionable': {'follows': [proposalv1["path"]]}}}
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

