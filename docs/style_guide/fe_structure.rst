Frontend Structure
==================

Module Systems
--------------

The adhocracy frontend is based mainly on two technologies: TypeScript
and angular.js. Both have their own module system. These two systems
are very different.

TypeScript Modules
++++++++++++++++++

In TypeScript, each file is a module (TypeScript does in fact offer two
module systems. We use `external modules
<http://www.typescriptlang.org/Handbook#modules-going-external>`_).
A module ``example.ts`` can be imported like this::

    import Example = require("./example");

Static imports have the benefit of allowing to check for the existence
of modules and for circular imports at compile time. But be aware that
this is only true if you actually use the module for more than
type-checking. If not, the import will be stripped after that step and
no further checks will be done.

An important bit is that these imports are responsible for actually
loading the required files in the browser. Without a non-stripped
import, the module will just not be available.

Angular Modules
+++++++++++++++

`Angular modules <http://docs.angularjs.org/guide/module>`_ are the
place where services, directives and filters are registered. When a
module depends on another one that means that it imports all of its
services, directives and filters.

A module ``example`` that depends on module ``dependency`` is created
like this::

    var exampleModule = angular.module("example", ["dependency"]);

This mechanism happens at runtime and therefore missing dependencies and
circular imports can only be detected at runtime.

.. FIXME: Angular modules have some major downsides:

   - They hide which services, directives and filters actually are
     registered
   - They need an additional name
   - They can not really be used with widgets because widget directives
     can only be defined where we know widgets *and* adapters.

How we use it
-------------

Packages
++++++++

In adhocracy we create what we call a *package* for every reusable
feature. A package may contain services, directives and filters. Each
package has its own folder in ``Packages/``.

A package may contain arbitrary TypeScript modules. But it is always
required to contain a TypeScript module with the same name as the
package. This TypeScript module wires all contents of the package into
an angular module.

This angular module is exposed by a variable ``moduleName`` and a
function ``register``. ``moduleName`` contains the name that should be
used for this module. By convention the module name is the package name
in camel case prefixed with 'adh'.  ``register`` takes angular as a
first argument and registers the module with all of its services and
directives.

.. FIXME: Packages should also include all CSS and other static content
   they depend on.

A package must not directly use TypeScript modules from other Packages.
When you want to actually use the code from other packages, you must
import the corresponding angular module referenced by the TypeScript
module's ``moduleName`` variable. This way it is also made sure that
requirejs will actually load the code.

.. FIXME: We might want to have exceptions, e.g. Util

Resources
+++++++++

The backend defines a set of resource and sheet types and exposes them
in a meta API. Matching TypeScript classes can be generated using a
script. Because we need a running backend to generate that code it is
checked into version control.

The resource definitions exist in a top level folder called
``Resources/``.

Adapters
++++++++

The concept of adapters is outlined in :doc:`generic_widgets`. They glue
together UI widgets with resource types. They are defined alongside the
generated resource code. So for a resource file ``Proposal.ts`` there is
a corresponding ``ProposalAdapters.ts`` that contains the adapters to
all widgets.

Applications
++++++++++++

At the top level of the directory structure there are TypeScript modules
that define angular modules. These represent different application. Each
application wires together everything that is required: Packages,
resources and adapters.

Application modules are also in charge of loading all required files. As
explained before, it is not sufficient to require the corresponding
TypeScript modules. You additionally need to use this modules, e.g. as
parameters to a dummy function like this::

    var forceLoad = (...args) => args;

Further Reading
---------------

- `Angular Best Practice for App Structure <https://docs.google.com/document/d/1XXMvReO8-Awi1EZXAXS4PzDzdNvV6pGcuaF4Q9821Es/pub>`_
- `An AngularJS Style Guide for Closure Users at Google <https://google-styleguide.googlecode.com/svn/trunk/angularjs-google-style.html>`_
