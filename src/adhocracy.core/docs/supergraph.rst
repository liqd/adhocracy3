
The Supergraph
==============


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
    A conglomerate of references and nodes that have a certain meaning. A relation is a pattern of nodes and references (of certain types) that can be found in graphs. (See below for examples.)

.. This could be:
 * a classic binary relation (Subject <- R -> Object)
 * simply a labelled reference (->)
 * something more complex and/or specialized (A <- Contradiction1 -> B, User1 <- marks_as_correct -> Contradiction1)


.. todo
    find better names!

.. ``reference-to-one``
    References which exist only once, e.g. the object reference in a predicate
    relationship

.. ``reference-to-many``
    References exists zero to many times, e.g. parts of collections

.. ``required reference``
    A reference from A to B, where the node A could not exist without its
    relationship to B.

.. ``optional reference``
    A reference from A to B, where the node A would still make sense without its
    reference to B.



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

Example 1.0:

.. digraph:: graph_1

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    statement -> substatement [label = contains];

    node [color = red];

    "statement'" -> statement [label = follows, color = red, style = dashed];


The outgoing references will be copied automatically to point
to the old referred nodes.

Example 1.1:

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains, color = red];

Incoming references have to be treated specially:



Nodes that are the ``dependents`` of the modified node are marked with a pending marker.

Example 1.2:

.. digraph:: graph_2

    agrees_with -> user [label = "subject"];
    agrees_with -> statement [label = "object"];
    agrees_with [color = grey];
    statement -> substatement [label = contains];
    "statement'" -> statement [label = follows, style = dashed];
    "statement'" -> substatement [label = contains];


These nodes are notified and have three options:

* They can confirm the changeset. This means they will be copied and their outgoing references will point to the new versions of the referred nodes. The old version will leave the pending state.

  Example 1.3:

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

  Example 1.4:

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

Example 2.0:

.. digraph:: graph42

    "A'" -> A [label = follows, style = dashed];
    Fork -> A [label = follows, style = dashed];
    "Fork'" -> Fork [label = follows, style = dashed];
    "A''" -> "A'" [label = follows, style = dashed];
    "A''" -> "Fork'" [label = follows, style = dashed];


Deletion
~~~~~~~~

In many cases, deletion can be represented in the graph by modifying a referring node and remove some outgoing edges. It is not necessary to delete the referred node.

Example 3.0:

.. digraph:: graph52

    Document -> A [label = contains]
    Document -> B [label = contains]
    Document -> C [label = contains]

    "Document'" [color = red];
    "Document'" -> Document [label = follows, color = red, style = dashed];
    "Document'" -> A [label = contains, color = red]
    "Document'" -> B [label = contains, color = red]

In other cases, it might be necessary to directly delete a node. For this case a special ``deleted`` node is introduced:

Example 3.1:

.. digraph:: graph324

    Alice;
    likes -> Alice [label = subject];
    likes -> something [label = object];
    deleted [color = red];
    deleted -> likes [label = follows, color = red, style = dashed];


History manipulation
~~~~~~~~~~~~~~~~~~~~

In some cases it might be necessary to modify or delete existing nodes and references directly, bypassing the versioning mechanism. This violates the non-mutability property and can be seen as a manipulation of the version history.

These manual modifications of the graph have to be done very carefully and could be considered as administrative tasks.

A typical example for such an administrative task is the real deletion of a
node containing illegal content.


Relations
---------

We defined relations as a pattern of nodes and references that have a specified meaning. Here is an example of a very simple relation:

Example 5.0:

.. digraph:: bla

    SomeComment -> A [label = comments];

This ``comments`` relation captures the idea, that ``SomeComment`` comments on ``A``. Also, the direction of the used reference implies, that ``A`` is an essential part of the comment.

Here is another example of a slightly more complex relation:

Example 5.1:

.. digraph:: huhu

    likes -> SomeUser [label = subject];
    likes -> B [label = object];

This relation captures the fact, that ``SomeUser`` ``likes`` ``B``. Again the directed references imply something about the nodes: ``SomeUser`` and ``B`` are essential parts of this ``likes`` node.

Here is how you could model a list:

.. digraph:: list

    list -> A [label = "element {rank: 1}"];
    list -> B [label = "element {rank: 2}"];
    list -> C [label = "element {rank: 3}"];

The list relation allows you to store an ordered sequence of nodes. Again the direction of the used references implies that the elements are essential parts of the list.

Modelling Data by Relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The process of modelling your data is basically a process of defining relations. When defining a relation you always have to think about the direction of the used references. Here's a checklist that might help:

.. digraph:: simple

    A -> B [label = someReference]

If you define a relation where ``A`` refers to ``B`` in some manner, then the following should hold:

* It makes sense that ``B`` is an essential part of ``A``.
* A modification of B (creating a newer version ``B'``) potentially leads to a newer version of ``A`` (``A'``) by triggering an update notification. The class of ``A`` should know how to handle such an update notification: immediate automatic confirmation, immediate automatic rejection or keeping the pending state and taking means to gather a manual decision.
* No other nodes want to refer to the reference itself. If you want to be able to refer to something, you have to model it as a node. If you want to refer to the relation between ``A`` and ``B`` in our example, you have to add an additional node:

  .. digraph:: hyperedge

        A -> someRelation [label = subject];
        someRelation -> B [label = object];

  This way you still retain the idea that ``B`` is an essential part of ``A``.
* Look out for reference cycles. If you define relations that make reference cycles very likely, you should reconsider your modelling. The supergraph allows reference cycles, but they certainly smell bad. (See conjoined_nodes_.)

.. note::
    Nodes and relations are the means you have to model your data. Don't fall back on simple vertices (not nodes) or simple edges (not relations) for this.

A Common Pitfall
~~~~~~~~~~~~~~~~~~

If you model binary relations (something along the lines of "subject predicate object"), it's tempting to model the predicate as a single reference:

.. digraph:: singleReferenceBinaryRelation

    subject -> object [label = predicate]

However make sure this is really what you want: Is ``object`` an essential part of ``subject``? If not, you have to change this to:

.. digraph:: hyperEdgeBinaryRelation

    predicate -> A [label = subject];
    predicate -> B [label = object];

A non-exhaustive list of relations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Follows``
    This is the relation used to connect nodes to its predecessor or
    predecessors. This might be modelled like this (we are still undecided on this):

    .. digraph:: follows

        "A'" -> A [label = follows, style = dashed];

    ..  Implemented as a vertex with a reference to the new vertex and zero to many
        references to predecessor vertices. Normal follows relationships have one
        predecessor relation, new object creations have zero predecessors, while
        follow superrelations merging several vertices together have two or more
        predecessors.

        or:
        Scheme: ``Successor -> Follows -> Predecessor(s)``


``Deletions``
    Node deletion is realized as a unary relation connected to the deleted
    node.

    .. digraph:: deletion

        Deletion -> A [label = follows, style = dashed];

    ..  Scheme: ``Deletion -> Follows -> Node``


``Predicates``
    Predicates are classical subject-predicate-object relations (also called binary relations), expressible as a verb.

    .. digraph:: predicates

        predicate -> A [label = subject];
        predicate -> B [label = object];

    Example: ``comments``


``Collections``
    Collections contain parts.

    Implemented as a list vertex with references-to-many to parts

    .. digraph:: collections

        collection -> part_1 [label = element];
        collection -> part_2 [label = element];
        collection -> "etc..." [label = element];

    Example: ``Set``, ``List``


``Lists``
    Ordered collections.

    Implemented as a collection with ranked edges.

    .. digraph:: lists

        collection -> part_1 [label = "element {rank: 1}"];
        collection -> part_2 [label = "element {rank: 2}"];
        collection -> "etc..." [label = "element {rank: n}"];

    Example: ``Document``

``Conjoined Nodes``
    Nodes which essentially belong to each other. Once one node is updated, the
    other node has to be updated too and vice versa - the nodes are synchronised. This can be achieved through cyclic subgraphs.

    .. _conjoined_nodes:
    .. digraph:: conjoinedNodes

        R1 [label = dependsOn];
        R2 [label = dependsOn];
        A -> R1;
        R1 -> B;
        B -> R2;
        R2 -> A;

    Possible examples: Translations, Binational treaties.


``More complex relations``
    Example: Some discussion leads to a set of (proposed) changes.

    .. digraph:: complex

        Proposal -> D [label = discussion];
        Proposal -> C [label = original];
        Proposal -> "C''" [label = newVersion];
        "C''" -> "C'" [label = follows, style = dashed, color = grey];
        "C'" [color = grey];
        "C'" -> C [label = follows, style = dashed, color = grey];
