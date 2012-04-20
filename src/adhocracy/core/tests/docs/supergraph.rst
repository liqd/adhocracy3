
The Supergraph
==============

Bulbs
-----

We use bulbs to access the graph database on a low level. Some terms:

 * vertex   - a node in the graph db
 * edge     - a directed edge in the graph db, connecting to vertices
 * property - vertices and edges can have properties. These appear as fields
              in the marshalled python objects.

Non-Mutability
--------------

This section describes rules and properties that we define for adhocracy core. They are not enforced by the underlying db.

The properties contained in a vertex don't change after creation of a vertex. The same goes for properties of edges. Also, created vertices and edges don't ever get deleted.

Some (actually most) of the edges are special edges that we will call "references". A reference from A to B captures the idea, that B is somehow an essential part of A. Therefore, the set of outgoing references from a vertex is not allowed to change. The set of ingoing references can change. (The most common case for egdes that are not references is the follower relationship, see below.)

Some intuition
~~~~~~~~~~~~~~
Imagine you have a vertex, transitively follow all its outgoing references and collect all the resulting vertices. Usually, this will result in a tree of vertices. A reference means (as defined above) that the referenced vertices are an "essential part" of the referencing vertex. So our tree of vertices is something like a deep-copy and recursively includes all the essential parts of our root vertex.

(Cycles using references are also allowed, so you might not get a tree, but a graph. The graph will still be a deep-copy on the described sense.)



Versioning
 * simple vertex modification
    * follower edges
 * edge propagation
 * recursive inV vertex propagation
    * termination!
 * prop: a -> b
        means a is newer (or equally old) as b.
 * forking
 * merging
 * administrative tasks can possibly manipulate the history after the fact


Superrelations
--------------

Superrelations are relations between content nodes are implemented as vertices,
not as edges. This allows for relations referencing other relations, and for
relations with connections to more than two vertices (hyperedges).

Note: The term ``superrelation`` is not carved into stone.


A non-exhaustive list of types of superrelations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Predicates``
    Predicates are classical subject-predicate-object relations, expressible
    as a verb.

    Implemented as a relationship vertex with references to subject and object
    vertices ``(Subject <- Predicate -> Object)``.

    Example: ``comments``.


``Collections``
    Collections contain parts.

    Implemented as a list vertex with references to parts
    ``(Collection -> Part_1, Collection -> Part_2, ...)``.

    Example: ``Set``, ``List``.


``List``
    Ordered collection.

    Implemented as a collection with ranked edges.

    Example: ``Document``.


``Conjoint nodes``
    Nodes which essentially belong to each other. Once one node is updated, the
    other node has to be updated too - the nodes are synchronised.

    Scheme: ``(A -> R -> B, B -> R -> A)`` or other cycles.

    Possible examples: Translations, Binational treaties.
    

``Unary relations``
    Relations connected to only one vertex.

    Scheme: ``(R -> A)``

    Possible example: Deletions.


``More complex relations``
    Exampel: Some discussion leads to a set of (proposed) changes.
   
    Scheme: ``(D <- R -> C1, R -> C2, R C3)``

