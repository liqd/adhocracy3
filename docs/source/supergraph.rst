Concept: The Supergraph
=========================


Our Terminology
---------------

``node``
    Building blocks of Adhocracy participation processes.  Examples:
    "document", "user", "likes", "vote", etc.  Nodes can connect to
    other nodes using references (see below).  They are implemented as
    python objects.

``reference``
    A reference connects a source node to a target node.
    References have a specific label, like: "contains", "has_author", etc.
    There a two basic types:

    * ``reference-to-one``: References which exist only once

    * ``reference-to-many``: References exists zero to many times

    What constitutes a node and what constitutes a reference is a
    design decision made on the content design level.

    It is often convenient to talk about nodes as ``vertices`` and
    references as ``edges`` in a graph.

    References are implemented as python attributes containing object
    references. (The term "reference" exists both on the data model
    level and on the implementation level.) A reference can either
    connect to a target node, or to a container of target nodes (list,
    set, ...).

``essence``
    Some references are "essential" to a source node, and some are
    not.  The essence of a node is the total of all nodes in the
    transitive hull of all essential references (i.e. all target nodes
    of essential references, and all targets of the essential
    references of those target nodes, and so on).

    The concept of essence is important for change management and will
    be discussed in detail below.  The idea is that if a node Y is in
    the essence of node X, and Y changes, X "naturally" changes with
    Y.

``dependents``
    The inverse essence of a node up to reflexivity: A node X is a
    dependent of Y if Y is in the essence of X, but not X itself.

``content node``
    A node that is self-contained, i.e. it has no outgoing references.
    (Content nodes are the leaves of the reference graph.)

``follows``
    Change management is implemented by ``follows`` edges between
    nodes.  A node that changes in fact is copied into a new version
    that follows the previous version.  ``follows`` edges are NOT
    references (neither on the design level nor on the implementation
    level).

``head`` A node without outgoing ``follows`` edges

``fork`` A node with more than one outgoing ``follows`` edges.

``merge`` A node with more than one incomming ``follows`` edges.

``relation``
    A pattern of references and nodes that have a certain
    meaning. (See below for examples.)




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

PROPOSAL: Not sure if this is already the intention, but it might be enough
to have just one universal DELETED node (or NULL node) in the whole graph.
The DELETED node ``follows`` all nodes that have been deleted (multiple
predecessors). Any node that has been deleted points to the DELETED node as
its successor.

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


Implementation Notes
--------------------

.. Relation example:  something more complex and/or specialized (A <- Contradiction1 -> B, User1 <- marks_as_correct -> Contradiction1)

This paragraph is a summary of the data structure discussions on Fri
2013-07-19 and before.  The later sections are obsolete to a varying
extent.

Nodes are implemented as python objects, references as attributes.  In
addition to the attributes, there is a method:

.. code:: python

  refs(): { <attr> : <node> }

that returns a dictionary mapping python strings containing attribute
names to the resp. reference target nodes.  This is interesting
because not all attributes of the node object are references.

The dependents (inverse references, i.e. only direct dependents) are
represented by a method:

.. code:: python

  deps(): { <node> : { <interface> : [ <attr> ] } }

that returns a dictionary mapping nodes to dictionaries, which in turn
map interfaces to lists of reference names (references are implemented
as attributes containing python references).

This way, it is easy to ask an object which other objects are
referencing it.

Alternatively dependents could be implemented as:

.. code:: python

  deps(): [ (<node>, <interface>, <attr>) ]

There should probably also be transitive hulls for references and
dependents, e.g. ``trans_refs()`` and ``trans_deps()``, which can be
implemented easily in terms of the above methods.  (XXX: is it more
pythonic to say "function" instead of "method"?)

Change management is modelled by nodes being copied into ``follows``
nodes.  There is a number of meaningful and desirable ways in which
references can react to changes in referenced and dependent nodes.

If a reference is essential, the target must notify the source of the
reference.  The source then has three options:

 * create a new version itself, keep the old reference unchanged, and
   update the reference in the new version to point to the new version
   of the target.  Example: if a paragraph in a document has been
   updated, the document should be considered updated as well.

 * ask the user what to do about the change.  Example: If a user
   "likes" a node, and the node changes, the user should be able to
   decide whether she also likes the new version, or only the previous
   version.

 * ignore the change, keep the reference pointed to the old version of
   the target, and do nothing.  Example: Change suggestions: a user wants
   to express that she would support a proposal if some changes are made.
   This change suggestion refers to one version of the proposal and shouldn't
   be updated to newer versions.

If a reference is not essential, things get more complicated.  The
source node will still be notified of any change in any target (it
always is for all references), but it has more freedom of choice in
what to do, and with that comes more confusion.  Example:

.. digraph:: graph101

  topic1 -> doc1 [label = "touched by"]
  topic1 -> doc2 [label = "touched by"]
  topic2 -> doc3 [label = "touched by"]
  topic2 -> doc4 [label = "touched by"]
  topic2 -> doc2 [label = "touched by"]

If topics (in wikimedia-speak: categories) are modelled this way,
neither of the options of essiential references are desirable, because
we would always create a new follower node of any topic that touches
any document that has a new version.  We either want to reference only
the head of each document, and always update all references whenever
documents are updated, or we want to reference all versions in the
history of the document.  (If we only reference heads, then what
happens if somebody keeps badges or comments or whatnot on the old
version, refusing to update?  Then the old document, still referenced
by the comment, falls out of the topic category.  Hum.  I think topic
references would need to be copied, not moved.  This would cause a lot
of references.  Perhaps references should be modelled the other way
round, not as "touched by", but as "touches".  But I digress.)

But if we simply keep track of the head of each document, what happens
with forks?  In a naive implementation, only the head created earliest
would keep the topic, and all forks would miss it, because the node
from which they fork would have passed on the reference to the
follower already.

Disallowing target node forks may be sometimes an option, but in this
case it is not.  So there has to be another notification event: If a
node is forked (has one or more followers already, and gets another
one), all follower nodes are traversed, and all dependents of those
nodes are notified of the fork.

The dependents can then decide what to do.  In the topic model above,
the topic node has to visit the new head and reference it as well,
without killing the old reference.  In other cases, it may raise an
exception and thereby disallow forks in target nodes.

This means that some node types are forkable and others are not.
Nodes therefore need an attribute:

.. code:: python

  forkable : bool

Because essential edges guarantee immutability of target nodes, they
are to be preferred over non-essential nodes when modelling
application data.  The following model:

.. digraph:: graph102

  likes -> user;
  likes -> doc [color = blue];

(Essential egdes are blue.)

has a non-essential edge, i.e. the clear update rules of essentiality
do not apply when the user updates her email address.  The following
model gets by with only essential edges:

.. digraph:: graph103

  user -> uid [color = blue];
  likes -> uid [color = blue];
  likes -> doc [color = blue];



XXX: Isn't change management of graph data structures a problem that
somebody has figured out on a theoretical level yet?




