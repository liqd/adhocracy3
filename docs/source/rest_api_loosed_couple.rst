Adhocracy 3 loosed coupling REST-API with substance-d backend
-------------------------------------------------------------

GET /instance/app/w/test
content::

    meta:
        id: test
        maininterface: IParteiProgramm
        content-type-id: parteiprogramm
        content-type-name: Partei-Programm
        node-state: pending
        workflow-state: public
        creator: /users/principe1
        creation-date: 16.01.2013 16:33

    data:
        IParteiProgramm:
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
        [p1, "Paragraph-Title", "paragraph", "pending", "public"]

        [p2, "Paragraph-Title", "paragraph", "head", "public"]

        ...

HEAD /instance/app/w/test::

    Get only meta data

OPTIONS /instance/app/w/test::

    GET: [IParteiProgramm, IVersionable, IContents, ILikable]
    PUT: [IParteiProgramm, IVersionable, IContents]
    POST: [Paragraph, Location, Image]   NOTE: addable content types

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
