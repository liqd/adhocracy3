Concept: Simulating Patches with The Supergraph
================================================


I think, we can simulate the patch ideas and interface while
sticking to model everything **not** as patches but as
document versions in the supergraph. We need:

- to divide data into smaller structured parts (but we
  wanted to do that anyway),
- intelligently consider ``follows``-edges.

Imagine, you have a Document with two paragraphs:

.. digraph:: graph_1

    D -> P1 [label = "1"];
    D -> P2 [label = "2"];

If someone creates a new version of ``P1`` we get a new
version of D (by essence propagation):

.. digraph:: graph_2

    D -> P1 [label = "1"];
    D -> P2 [label = "2"];

    "D'" -> "P1'" [label = "1"];
    "D'" -> "P2"  [label = "2"];

    "P1'" -> P1 [color = blue];
    "D'" -> D   [color = blue];

(``follows``-edges are blue.)

Now while looking at ``D'`` someone modifies ``P2``. Once
again we get a new version ``D''``:

.. digraph:: graph_2

    D -> P1 [label = 1];
    D -> P2 [label = 2];

    "D'" -> "P1'" [label = 1];
    "D'" -> "P2"  [label = 2];

    "D''" -> "P1'" [label = 1];
    "D''" -> "P2'" [label = 2];

    "P1'" -> P1   [color = blue, label = p];
    "D'"  -> D    [color = blue, label = q];
    "P2'" -> P2   [color = blue, label = r];
    "D''" -> "D'" [color = blue];

If you now look at ``D`` and its essence you have three
``follows``-edges to consider, labelled ``p``, ``q`` and
``r``. ``r`` is the interesting one here. It should be no
problem to build an interface that allows you to pull in 
``P2'`` into ``D`` and thereby creating a new version of
``D`` (called ``E``) that didn't exist before:

.. digraph:: graph_2

    D -> P1 [label = 1];
    D -> P2 [label = 2];

    "D'" -> "P1'" [label = 1];
    "D'" -> "P2"  [label = 2];

    "D''" -> "P1'" [label = 1];
    "D''" -> "P2'" [label = 2];

    E -> P1    [label = 1];
    E -> "P2'" [label = 2];

    "P1'" -> P1   [color = blue];
    "D'"  -> D    [color = blue];
    "P2'" -> P2   [color = blue];
    "D''" -> "D'" [color = blue];
    E     -> D    [color = blue];

This version ``E`` implicitly existed as a possibility once
``P2'`` was created. It can be created ephemerally to be
looked at in an interface and it can be brought into
existence (in the supergraph) if someone considers ``E``
relevant.

Isn't that great?

Now here is something even darcs cannot do (in one text
file):

Imagine someone changes the order of the paragraphs
in ``D''``, (``E`` is removed for clarity):

.. digraph:: graph_2

    D -> P1 [label = 1];
    D -> P2 [label = 2];

    "D'" -> "P1'" [label = 1];
    "D'" -> "P2"  [label = 2];

    "D''" -> "P1'" [label = 1];
    "D''" -> "P2'" [label = 2];

    "D'''" -> "P2'" [label = 1];
    "D'''" -> "P1'" [label = 2];

    "P1'" -> P1     [color = blue, label = p];
    "D'"  -> D      [color = blue];
    "P2'" -> P2     [color = blue, label = q];
    "D''" -> "D'"   [color = blue];
    "D'''" -> "D''" [color = blue, label = r];

We look at ``D'''``, its essence and all the
``follows``-edges, again labelled ``p``, ``q`` and ``r``.
Reverting ``r`` is trivial and would just revert the change
and lead to ``D''`` which already exists. But an interface
could allow you to try out a version where the paragraphs'
order is changed, but ``P2'`` (for example) is reverted to
``P2`` (via ``q``, creating ``F``):

.. digraph:: graph_2

    D -> P1 [label = 1];
    D -> P2 [label = 2];

    "D'" -> "P1'" [label = 1];
    "D'" -> "P2"  [label = 2];

    "D''" -> "P1'" [label = 1];
    "D''" -> "P2'" [label = 2];

    "D'''" -> "P2'" [label = 1];
    "D'''" -> "P1'" [label = 2];

    F -> P2 [label = 1];
    F -> "P1'" [label = 2];

    "P1'" -> P1     [color = blue];
    "D'"  -> D      [color = blue];
    "P2'" -> P2     [color = blue];
    "D''" -> "D'"   [color = blue];
    "D'''" -> "D''" [color = blue];
    F -> "D'''"     [color = blue];
