
The Supergraph
==============

.. note::
    **Warning: This is a draft. We are currently working on this document.**


Our Terminology
---------------

``vertex``
    a node in the graph db

``edge``
    a directed edge in the graph db, connecting to vertices

``property``
    vertices and edges can have properties. These appear as fields in the
    marshalled python objects.

``reference``
    Some (actually most) of the edges are special edges that we will call
    "references". A reference from A to B captures the idea that B is somehow an
    essential part of A. References have labels to distinguish different types.

``required reference``
    A reference from A to B, where the node A could not exist without its
    relationship to B.

``optional reference``
    A reference from A to B, where the node A would still make sense without its
    reference to B.

``node``
    a vertex that can be referenced and can itself reference other nodes. Every node has a name that uniquely identifies the node.

``content node``
    a node that is self-contained, i.e. it has no outgoing references (with the
    possible exception of ``follows``-references)

``essence``
    an essence for a given node is the sub-graph that contains the node itself
    (the root node of the essence) and all transitively referenced nodes. (An
    essence for a given node is immutable, see below.)

``dependents``
    something like an inverse essence: the sub-graph of nodes that transitively refer to a given node, excluding that given node.

``relation``
    A conglomerate of references and nodes that have a certain meaning. A relation is something like a pattern of nodes and references (of certain types) that can be found in graphs. (See below for examples.)

.. This could be:
 * a classic binary relation (Subject <- R -> Object)
 * simply a labelled reference (->)
 * something more complex and/or specialized (A <- Contradiction1 -> B, User1 <- marks_as_correct -> Contradiction1)


.. _todo::
    find better names!

.. ``reference-to-one``
    References which exist only once, e.g. the object reference in a predicate
    relationship

.. ``reference-to-many``
    References exists zero to many times, e.g. parts of collections


Non-Mutability
--------------

.. note::
    This section describes rules and properties that we define for adhocracy
    core. They are not enforced by the underlying db.

The properties contained in a node don't change after creation of the node. The
same goes for properties of references. Also, created nodes and references don't
ever get deleted.

The set of outgoing references from a node is not allowed to change. The set of
incoming references can change. This also means that a reference from A to B
implies that A is younger or equally old than B.

Some Intuition
~~~~~~~~~~~~~~

Imagine you have a node, transitively follow all its outgoing references and
collect all the resulting nodes. This gives you the node's ``essence``. Usually,
this will result in a tree of nodes. A reference means (as defined above) that
the referenced nodes are an "essential part" of the referencing node. So our
tree of nodes is something like a deep-copy and recursively includes all the
essential parts of our root node.

(Cycles using references are also allowed, so you might not get a tree, but a
sub-graph. This sub-graph will still be a deep-copy in the described sense.)


Versioning
----------

As existing nodes in the graph never change, every node modification creates a new node which is connected to the originating node with a ``follows`` relation. (We haven't decided how to implement this follows relation -- it might be a reference or a node. In the following example graphs the ``follows`` relation is represented by a dashed arrow.)


Example:

.. digraph:: graph_1

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    statement -> substatement [label = contains];

    node [color = red];

    "statement'" -> statement [label = follows, color = red, style = dashed];

The outgoing references will be copied automatically to point
to the old referred nodes.

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains, color = red];

Incoming references have to be treated specially:



Nodes that are the ``dependents`` of the modified node are marked with a pending marker.

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    agrees_with [color = grey];
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains];


These nodes are notified and have three options:

* They can confirm the changeset. This means they will be copied and their outgoing references will point to the new versions of the referred nodes. The old version will leave the pending state.

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    "agrees_with'" -> agrees_with [label = "follows", style = dashed, color = red];
    "agrees_with'" -> user [label = "subject", color = red];
    "agrees_with'" -> "statement'" [label = "object", color = red];
    "agrees_with'" [color = red];
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains];

* They can reject the changeset. This means, they will leave the pending state, but no new nodes nor references get created. The outgoing references of the formerly pending node will not change and point to old versions of nodes.

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    agrees_with;
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains];

* They can do nothing and keep the pending state. At any later point in time a node can reject or confirm a changeset, probably triggered by some external event, e.g. user interaction.


Forking and merging
~~~~~~~~~~~~~~~~~~~

Modeling versioning in this manner also allows for forking and merging:

.. digraph:: graph42

    "A'" -> A [label = follows, style = dashed];
    Fork -> A [label = follows, style = dashed];
    "Fork'" -> Fork [label = follows, style = dashed];
    "A''" -> "A'" [label = follows, style = dashed];
    "A''" -> "Fork'" [label = follows, style = dashed];

Deletion
~~~~~~~~

In many cases, deletion can be represented in the graph by modifying a referring node and remove some outgoing edges. It is not necessary to delete the referred node.

.. digraph:: graph52

    Document -> A [label = contains]
    Document -> B [label = contains]
    Document -> C [label = contains]

    "Document'" [color = red];
    "Document'" -> Document [label = follows, color = red, style = dashed];
    "Document'" -> A [label = contains, color = red]
    "Document'" -> B [label = contains, color = red]

In other cases, it might be necessary to directly delete a node. For this case a special ``deleted`` node is introduced:

.. digraph:: graph324

    Alice;
    likes -> Alice [label = subject];
    likes -> something [label = object];
    deleted [color = red];
    deleted -> likes [label = follows, color = red, style = dashed];


.. note::
    **The rest of this document is not finished! It will change
    fundamentally!!!**

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

Superrelations are relations between vertices that are implemented as vertices
themselves, not as edges. This allows for relations referencing other relations,
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


``Conjoints Nodes``
    Nodes which essentially belong to each other. Once one node is updated, the
    other node has to be updated too - the node are synchronised.

    Scheme: ``A -> R -> B, B -> R -> A`` or other cyclic subgraphs.

    Possible examples: Translations, Binational treaties.


``More complex relations``
    Exampel: Some discussion leads to a set of (proposed) changes.

    Scheme: ``D <- R -> C1, R -> C2, R C3``

