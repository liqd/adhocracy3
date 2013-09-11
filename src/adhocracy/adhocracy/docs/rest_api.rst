Adhocracy 3 loosed coupling REST-API with substance-d backend
=============================================================

Prerequist ::
--------------

    >>> import requests
    >>> import json
    >>> from pprint import pprint
    >>> from webtest import TestApp
    >>> from adhocracy.testing import config
    >>> from adhocracy import main
    >>> app = main({}, **config)
    >>> testapp = TestApp(app)


Working with Pool content
-------------------------

OPTIONS ::

    >>> resp = requests.options("http://localhost:6541/adhocracy")
    >>> pprint(resp.json())
    {'GET': ['adhocracy.interfaces.IName'],
     'HEAD': [],
     'POST': ['adhocracy.interfaces.INodeContainer',
              'adhocracy.interfaces.IPool',
              'adhocracy.interfaces.IProposalContainer'],
     'PUT': ['adhocracy.interfaces.IName']}

HEAD ::

    >>> resp = requests.head("http://localhost:6541/adhocracy")
    >>> headers = [x for x in resp.headers]
    >>> headers.sort()
    >>> headers
    ['content-length', 'content-type', 'date', 'server']
    >>> resp.text
    ''


GET::

    >>> resp = requests.get("http://localhost:6541/adhocracy", )
    >>> pprint(resp.json())
    {'children': [],
     'content_type': 'adhocracy.interfaces.IPool',
     'data': {'adhocracy.interfaces.IName': {'name': ''}},
     'meta': {'content_type': 'adhocracy.interfaces.IPool',
              'content_type_name': 'adhocracy.interfaces.IPool',
              'creation_date': '',
              'creator': '',
              'name': 'adhocracy',
              'oid': 8339204787337977585,
              'path': '/adhocracy',
              'workflow_state': ''}}


PUT::

    >>> data = {'content_type': 'adhocracy.interfaces.IPool',
    ...         'data': {'adhocracy.interfaces.IName': {'name': 'NEWTITLE'}}}
    >>> resp = requests.put("http://localhost:6541/adhocracy", data=json.dumps(data))
    >>> pprint(resp.json())
    {'path:': '/adhocracy'}

    >>> data['data'] = {'adhocracy.interfaces.IName': {'name': ''}}
    >>> resp = requests.put("http://localhost:6541/adhocracy", data=json.dumps(data))



POST:

    >>> data = {'content_type': 'adhocracy.interfaces.IProposalContainer',
    ...         'data': {'adhocracy.interfaces.IName': {'name': 'proposal1'}}}
    >>> resp = requests.post("http://localhost:6541/adhocracy", data=json.dumps(data))
    >>> pprint(resp.json())
    {"path": "/adhocracy/proposal1...


Interfaces ::

     ..data:
        ..IDocument:
            ..title:  Title
            ..description: Bla
        ..IVersionable:
            ..follows:
                ../instances/spd/w/test0
            ..followed_by:
                ../instances/spd/w/test1
                ../instances/spd/w/test2
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

    >>> resp = requests.get("http://localhost:6541/adhocracy/proposal1/_versions")
    >>> pprint(resp.json()["children"])

The initial node without follows nodes is already there ::



If we change this node we create a new version ::

NOTE: PUT for INode content is not idempotent this breaks the REST architecture principles



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
