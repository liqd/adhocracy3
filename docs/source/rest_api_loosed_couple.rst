Adhocracy 3 loosed coupling REST-API with substance-d backend
-------------------------------------------------------------

GET /instance/app/w/test
content::

    content_type: IParteiProgramm

    meta:
        id: test
        path: "/instances/spd.."
        content_type: IParteiProgramm
        content_type-name: Partei-Programm
        workflow_state: public
        creator: /users/principal1
        creation_date: 16.01.2013 16:33
        ..
    data:
        IDocument:
            title:  Title
            text: Bla
        IVersionable:
            follows:
                /instances/spd/w/test0
            followed_by:
                /instances/spd/w/test1
                /instances/spd/w/test2
        IContents:
            contents:
                /instances/spd/w/test/p1
                /instances/spd/w/test/p2
                ...
        ILikable
            liked:       NOTE: this can be a huge list, better use the supergraph reference search or just show a number
               /users/1
               /users/2
               ...

    children:            NOTE: this can be huge
        {id: test, path: "/instance", ..}
elf.context.values(       ...

HEAD /instance/app/w/test::

    Get only meta data


POST/PUT /instance/app/w/test
content::

    content_type: IParteiProgramm

    data:
        IDocument:
            title:  Title
            text: Bla
        ...

OPTIONS /instance/app/w/test::

    GET: [IDocument, IVersionable, IContents, ILikable]
    PUT: [IDocument, IVersionable, IContents]
    POST: [IPargraph, IText, ILocation, IImage]   NOTE: addable content types

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
