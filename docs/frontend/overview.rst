Overview
========

The adhocracy 3 frontend is an opinionated web framework based on
angular.js and written in TypeScript. Its main goal is to provide all
the building blocks that developers need to implement participation
processes of all kinds. The user interface should be consistent and
recognizable while providing enough flexibility for a wide range of
target audiences as well as branding.

Angular
-------

`AngularJS <https://angularjs.org/>`__ is an open source JavaScript
framework mainly developed by Google.

In contrast to traditional frameworks like jQuery, you do not directly
interact with the DOM. Instead, you only interact with data structures
in JavaScript. The DOM is *bound* to these data structures and updates
automatically.

Other notable features are `services
<https://docs.angularjs.org/guide/services>`_ (singleton objects),
`dependency injection <https://docs.angularjs.org/guide/di>`_ (a way
to decouple your code), and *promise based APIs* (as opposed to
callbacks).

Angular is somewhat similar to other client-side rendering frameworks
like `ember.js <http://emberjs.com/>`__ or
`react <http://reactjs.com/>`__.

TypeScript
----------

`TypeScript <http://www.typescriptlang.org/>`__ is an open-source
language mainly developed by Microsoft.

It contains many features of upcoming JavaScript versions (ES6/7) as
well as static typing while staying compatible with ES5. Notable
features include:

-  static type checking
-  module system
-  classes
-  arrow functions
-  default values for function arguments

In order to use static type checking with non-TypeScript code, the
project `DefinitelyTyped <http://definitelytyped.org/>`__ provides type
definitions for many popular JavaScript libraries.

TypeScript is similar to `CoffeeScript <http://coffeescript.org/>`__ in
that it compiles to JavaScript. It is similar to
`Babel <https://babeljs.io/>`__ in that it backports many future
JavaScript features.

Backend API
-----------

Sheets
++++++

:ref:`Resources <api-resource-structure>` in adhocracy are composed of
*sheets*. Each sheet describes one aspect of the resource, e.g. that it
has a title (``ITitle``) or that it can be rated (``IRateable``) or
commented on (``ICommentable``).

Which sheets are available or required on a resource is defined by their
*content type*. You can get a list of all content types and their sheets
from the :ref:`meta-api`.

Pool queries
++++++++++++

All resources that can contain other resources have an ``IPool`` sheet
and are generally refered to as pools. Pools can be :ref:`queried
<api-pool-queries>` for their contents. The results can be sorted and
filtered by several conditions, some of which depend on the available
sheets. Example: In order to get all comments that refer to resource
``/my/resource``, you may use the following (simplified) query string::

    ?depth=all&content_type=IComment&IComment:refers_to=/my/resource&sort=creation_date

Deletion
++++++++

In order to always allow users to recover from accidental actions, the
backend does not physically delete content. This is why the ``DELETE``
HTTP method is generally not available. Instead, there are :ref:`ways to
mark the content as deleted <api-deletion>` so it is no longer
accessible.

Batch requests
++++++++++++++

Sometimes you may want to change data in the backend, but it is not
possible to do it in a single request. Doing it in two or more requests
however has the risk that you end up with an inconsistent state because
one of the later requests fails.

For this case, the adhocracy backend allows to encode several requests
in a single :ref:`batch request <batch-requests>` that is then processed
in a single database transaction. This way the whole batch is rolled
back if a single request fails.

Permissions
+++++++++++

The backend has a sophisticated :ref:`permission system
<api-permission-system>` with roles, groups and local permissions. The
frontend ignores all this and is only interested in the result: Is the
current user allowed to do this action? All information required for
that can be obtained by sending an :ref:`OPTIONS request
<meta-api-options>` to the relevant backend endpoint.

Websockets
++++++++++

The backend uses :ref:`websockets <api-websockets>` to notify the
frontend whenever a resource changes. This can be used to update the UI
automatically.

.. NOTE::

   Updating the UI automatically is possible, but not always the right
   thing to do. If everything is changing all the time, users will only
   get confused.

.. NOTE::

   Websocket notifications are also used to do cache invalidation in the
   frontend. So if the websocket connection fails, the frontend stops
   caching completely and may get slow.

The build directory
-------------------

Adhocracy is split into several python packages. For a specific project
there are typically four packages:

==============  ==================  =============  ========
             Core                        Customization
----------------------------------  -----------------------
Backend         Frontend            Backend        Frontend
==============  ==================  =============  ========
adhocracy_core  adhocracy_frontend  adhocracy_foo  foo
==============  ==================  =============  ========

When bin/buildout is run, the ``static`` directories from both frontend
packages are merged into a single one called ``build`` that is located
next to ``static`` in the customization package.  Merging in this case
means that files from both directories are symlinked into the build
directory. If a file exists in both packages, the one from the
customization overwrites the one from core.

.. NOTE::

   This mechanism allows the customization to replace any file from
   core. However, this is strongly discouraged in most cases as it is
   hard to maintain the overwrites.

Independent widgets
-------------------

In order to provide reusable widgets, we try to make our directives as
independent as possible. In practice that means that we always isolate
the directive scope (with few exceptions) and pass a minimal number of
parameters.

For example, a proposal directive would only get the ``path`` of a
resource instead of relying on some parent directive to fetch it first.
This of course means that many directives may trigger the same HTTP
requests. This is mitigated by a caching system that is built into the
``adhHttp`` service.
