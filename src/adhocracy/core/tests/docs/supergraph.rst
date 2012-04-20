
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

superrelations
 * relations as vertices
   * referencing relations
   * relations of more than two vertices (so called hyper-edges)
 * non-exhaustive list of types of relations
   * classic, referencing relationship (A <- R -> C) (subject, object)
     * expressible as verbs
     * comments
   * containers, referencing (R -> A, R -> B, ...)
     * possibly ranked edges for orderings
     * document containing list of statements
   * synchronized nodes (A -> R -> B, B -> R -> A / cycles)
     * Translations
   * unary relations (R -> A)
   * more complex relations
     * some discussion leads to a set of (proposed) changes (D <- R -> C1, R -> C2, R C3)

example for doctests:
    >>> 42
    42
