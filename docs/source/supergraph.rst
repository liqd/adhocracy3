
The Supergraph
==============

Bulbs
-----

We use bulbs_ to access the graph database on a low level. Some terms:

``vertex``
    a node in the graph db

``edge``
    a directed edge in the graph db, connecting to vertices

``property``
    vertices and edges can have properties. These appear as fields in the
    marshalled python objects.

.. _bulbs: http://bulbflow.com


Non-Mutability
--------------

This section describes rules and properties that we define for adhocracy core.
They are not enforced by the underlying db.

The properties contained in a vertex don't change after creation of a vertex.
The same goes for properties of edges. Also, created vertices and edges don't
ever get deleted.

Some (actually most) of the edges are special edges that we will call
"references". A reference from A to B captures the idea that B is somehow an
essential part of A. Therefore, the set of outgoing references from a vertex is
not allowed to change. The set of incoming references can change. This also
means that a reference from A to B implies that A is younger or equally old
than B.

There are two types of references: 

.. todo::
    find better names!

``reference-to-one``
    References which exist only once, e.g. the object reference in a predicate
    relationship

``reference-to-many``
    References exists zero to many times, e.g. parts of collections

Some intuition
~~~~~~~~~~~~~~

Imagine you have a vertex, transitively follow all its outgoing references and
collect all the resulting vertices. Usually, this will result in a tree of
vertices. A reference means (as defined above) that the referenced vertices are
an "essential part" of the referencing vertex. So our tree of vertices is
something like a deep-copy and recursively includes all the essential parts of
our root vertex.

(Cycles using references are also allowed, so you might not get a tree, but a
graph. The graph will still be a deep-copy in the described sense.)

Versioning
----------

As objects (vertices and edges) in the graph never change, every object
modification creates a new vertex which points to the originating vertex with a
``follows`` relation.


Example:

.. digraph:: graph_1

    agrees_with -> user;
    agrees_with -> statement;
    statement -> substatement [label = contains];

    node [color = red];

    "statement'" -> statement [label = follows, color = red];

The outgoing references will be copied automatically to point
to the old referred vertices. 

.. digraph:: graph_2

    agrees_with -> user;
    agrees_with -> statement;
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows];
    "statement'" -> substatement [label = contains, color = red];

.. note::
    The rest of the sections is not finished!)

Incoming references have to be treated specially:

Vertices that refer to the modified vertex, directly or transitively are marked
with a "potentially outdated" marker. These vertices are notified and can
decide by themselves if they are copied into new vertices with references to
the updated vertex.

.. digraph:: graph_3

    agrees_with -> user;
    agrees_with -> statement;
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows];
    "statement'" -> substatement [label = contains];
    node [color = red];
    "agrees_with'" -> user [color = red];
    "agrees_with'" -> "statement'" [color = red];
    "agrees_with'" -> agrees_with [label = follows, color = red];

To guarantee termination, update propagation has to be realized
transactionally.


Forking and merging
~~~~~~~~~~~~~~~~~~~

Modeling versioning in this manner also allows for forking and merging:

.. todo::
    include fork and merge graph examples

Deletion
~~~~~~~~

.. todo::
     * write in which cases deletion makes sence

     * Reference deletion

     * Vertex deletion is a special kind of versioning which creates a special
       ``deletion`` vertex pointing to the deleted vertex with a ``follows``
       edge.


History manipulation
~~~~~~~~~~~~~~~~~~~~

In some cases it might be modify or delete existing vertices and edges
directly, i.e. without using the versioning mechanism. This violates the
non-mutability property and can be seen as a manipulation of the version
history.

Manual modification of the graph have to be done very carefully and could be
considered as administrative tasks.

A typical example for such an administrative task is the real deletion of an
object containing illegal content.


Superrelations
--------------

Superrelations are relations between content nodes that are implemented as
vertices, not as edges. This allows for relations referencing other relations,
and for relations with connections to more than two vertices (hyperedges).

.. note::
    The term ``superrelation`` is not carved into stone.


A non-exhaustive list of types of superrelations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Follows``
    This is the relation used to connect vertices to its predecessor or
    predecessors.

    Implemented as a vertex with a reference to the new vertex and zero to many
    references to predecessor vertices. Normal follows relationships have one
    predecessor relation, new object creations have zero predecessors, while
    follow superrelations merging several vertices together have two or more
    predecessors.

    Scheme: ``Successor -> Follows -> Predecessor(s)``


``Deletions``
    Vertex deletion is realized as a unary relation connected to the deleted
    vertex.

    Scheme: ``Deletion -> Follows -> Node``


``Predicates``
    Predicates are classical subject-predicate-object relations, expressible
    as a verb.

    Implemented as a vertex with references to subject and object vertices.

    Scheme: ``Subject <- Predicate -> Object``

    Example: ``comments``


``Collections``
    Collections contain parts.

    Implemented as a list vertex with references-to-many to parts

    Scheme: ``Collection -> Part_1, Collection -> Part_2, ...``

    Example: ``Set``, ``List``


``Lists``
    Ordered collections.

    Implemented as a collection with ranked edges.

    Example: ``Document``


``Conjoint nodes``
    Nodes which essentially belong to each other. Once one node is updated, the
    other node has to be updated too - the nodes are synchronised.

    Scheme: ``A -> R -> B, B -> R -> A`` or other cyclic subgraphs.

    Possible examples: Translations, Binational treaties.
    

``More complex relations``
    Exampel: Some discussion leads to a set of (proposed) changes.
   
    Scheme: ``D <- R -> C1, R -> C2, R C3``

