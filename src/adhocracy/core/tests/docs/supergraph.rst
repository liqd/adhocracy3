
The Supergraph
==============

Non-Mutability
 * vertex properties
 * edge properties
 * things don't get deleted
 * outEs (except for follower)

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
