Softwarestack
=============

-   `Python 3 <https://www.python.org>`_ (programming language)

-   `Pyramid <http://pylonsproject.org>`_  (web framework)

-   `substance D <http://docs.pylonsproject.org/projects/substanced/en/latest>`_ (application server)

-   `hypatia <https://github.com/Pylons/hypatia>`_ (search)

-   `ZODB <http://zodb.org>`_ (object database)

-   `colander schema <http://docs.pylonsproject.org/projects/colander/en/latest/>`_ (data structures and validation)

-   `Autobahn|Python <http://autobahn.ws/python/>`_ (websocket server)

-   `Varnish <https://www.varnish-cache.org/>`_ (http proxy cache server)

-   `buildout <http://www.buildout.org/en/latest/>`_ (build system)


History
-------

We started 2012 with the plan to port adhocracy2 to pyramid.
This become a long discussion how to build a framework for particpation
processes based on fancy graph data structures :doc:`../attic/index.rst`.
Mid 2013 we started serious efforts to start developing.
We compared multiple framework - database combinations to find the right
technical base that allows to start quickly but does not stand in they way if
the project grows. Doing this we had the following in mind:

*    python 3 support
*    active community and good documentation
*    good extensibility -> `zope component` style like architecture
*    fast references to resources and complex reference queries
*    one system to search & store python objects and references
*    ACID transactions
*    resource tree, url traversal
*    workflows, local permissions

We did two prototypes to play with the neo4j graph database and dropped it
mainly due to cutting edge python support and transaction features.
So we came to the ZODB database. It is stable and can do python object
references in a very simple way because it is an object database.
That lead to using pyramid and substanced as small framework that matched many
of our requirements.

Evaluated framework - database combinations
-------------------------------------------

(restored version from mid 2013, original evaluation report is lost)

*General*

========================= ========  ================  =============  =========  ===========  ===============  ==============  ========  =============
feature:                  python 3  active developed  documentation  fullstack  simple code  admin interface  high level api  REST-API  extensibility (every behaviour can be extendend/replaces without changing the core code)
========================= ========  ================  =============  =========  ===========  ===============  ==============  ========  =============
cubicweb - sql            \-        \+                \+             \++        \-           \+               \++             \++       \+
django  - sql             \-        \+                \+             \++        \ -          \+               \++             \+        \+-
pyramid/kotti - sql       \+        \+                \+             \++        \+           \+               \+              \ -       \+
pyramid/bulbflow - neo4j  \+        \-                \+             \-         \+           \-               \+              \-        \-
pyramid - rexster/neo4j   \+        \+-               \+             \-         \-           \-               \+              \+        \+-
pyramid - ZODB            \+        \+                \-             \+         \-           --               \-              \-        \+
pyramid/substanced - ZODB \+        \+-               \+             \++        \+           \++              \+              \-        \+
Zope2/Plone - ZODB        \--       \+-               \-             \++        --           \+               \++             --        \++
ZTK/Grok - ZODB           \+-       \-                \+             \++        --           \+-              \+              --        \++
========================= ========  ================  =============  =========  ===========  ===============  ==============  ========  =============



*References*

========================= ===============================  ====   ===========
feature:                  complex queries/graph traversal  fast   scalibility
========================= ===============================  ====   ===========
cubicweb/sql              \++                              \+-    \++
django - sql              \-                               \+-    \+
pyramid/kotti - sql       \-                               \+-    \+
pyramid/bulbflow - neo4j  \++                              \-     \++
pyramid - rexter/neo4j    \++                              \--    \++
pyramid - ZODB            \-                               \++    \++
pyramid/substanced - ZODB \-                               \+     \++
Zope2/Plone - ZODB        \+                               \+-    \+-
ZTK/Grok - ZODB           \-                               \++    \++
========================= ===============================  ====   ===========


*Resources*

========================= ============ ============== =================  =========  ========   =================
feature:                  "sheets"     resource tree  local permissions  traversal  workflow   ACID transactions
========================= ============ ============== =================  =========  ========   =================
cubicweb/sql              \+            \-              \-                  \-         \-           \+
django - sql              \-            \-              \+-                 \-          ?           \+
pyramid/kotti - sql       \-            \+              \+                  \+          \+          \+
pyramid/bulbflow - neo4j  \-            \-              \-                  \-          \-          \+
pyramid - rexter/neo4j    \-            \-              \-                  \-          \-          \-
pyramid - ZODB            \-            \+              \+                  \+          \-          \+
pyramid/substanced - ZODB \+            \+              \+                  \+          \+          \+
Zope2/Plone - ZODB        \+            \+              \+                  \+          \++         \+
ZTK/Grok - ZODB           \+            \+              \+                  \+          \+          \+
========================= ============ ============== =================  =========  ========   =================


*Search*

========================= ================== ================ ================= =================
feature:                  checks permissions  full text index  attribute index  same transaction like resources
========================= ================== ================ ================= =================
cubicweb/sql              \-                   \++               \+              \-
django - sql              \-                   \++               \+              \-
pyramid/kotti - sql       \+                   \++               \+              \-
pyramid/bulbflow - neo4j  \-                   \-                \+              \-
pyramid - rexter/neo4j    \-                   \-                \+              \-
pyramid - ZODB            \-                   \-                \-              \-
pyramid/substanced - ZODB \+                   \+                \+              \+
Zope2/Plone - ZODB        \+                   \+                \++             \+
ZTK/Grok - ZODB           \+                   \+                \+              \+
========================= ================== ================ ================= =================


*Notes*

========================== ======================
========================== ======================
cubicweb                   SemanticWeb web framework
django                     full stack web framework
pyramid                    micro web framework, internally based on zope components
pyramid / kotti            small cms project
pyramid / bulbflow - neo4j Resource Modelling for graph database neo4j
pyramid - rexter / neo4j   REST-API for graph database neo4j
pyramid / substanced       small application server project
Zope2 / Plone              Big cms project/full stack framework based on zope components, permission checks enforced in application code
ZTK (ZopeToolkit) / Grok   full stack framework based on zope components, not active anymore, permission checks enforced in application code
========================== ======================

Other evaluated frameworks without ZODB: pyramid - cubicweb database, pyramid - rdflib, pyramid/repoze.workflow/plone.behavior - neo4j

Others with ZODB:  w20e.pycms,  Karl Project, pyramid/repoze.workflow/plone.behavior, Zope2/repoze.workflow/plone.dexterity

More recent frameworks not considered
-------------------------------------

If we start a rewrite we would focus on full-stack frameworks for REST-APIs,
standards, and simplified requirements. The following more recent projects
are look promising.

-   http://ramses.tech/

    -   full stack solution for REST-APIs
    -   easy prototyping/api specification
    -   good ElasticSearch "frontend" to handle all kind of requests

-   http://morepath.readthedocs.org/

    -   flexible micro framework for REST-API/HTML rendering
    -   combine/extend small application (like processXY, document management, user management, ...)

-   django rest framework v3 / (or json-api extension) http://www.django-rest-framework.org/

    -   full stack solution for REST-APIs

-   json-api https://py-jsonapi.readthedocs.org/en/latest/

    -   full stack solution for REST-APIs

-   http://pythonhosted.org/jsondata/

    -   data structure and patches based on JSON-Schema
