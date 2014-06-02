JavaScript Guidelines
=====================

General considerations
----------------------

-  this document is split in multiple sections

   -  general JavaScript
   -  Typescript
   -  Angular

      -  Angular templates

   -  Adhocracy 3
   -  Tests

-  We prefer conventions set by 3rd party tools (e.g. tsLint) over our
   own preferences.
-  We try to be consistend with other guidelines from the adhocracy3
   project

General JavaScript
------------------

-  strict mode
-  strict comparisons
-  semicolons
-  4 space indentation

TODO:

-  tsLint configuration

   -  https://github.com/palantir/tslint

-  allow chaining?

   -  where it might be useful:

      -  promises (``.then()``)
      -  angular registration

   -  if chaining is allowed: how should it be indented?

-  single or mutliple ``var``\ s
-  when to return promises

   -  wherever it might someday be useful
   -  only where absolutely needed

-  consistent alias for ``this``
-  alignment::

       foo = {a: 1,
              b: 2,
              c: 3}

   or::

       foo = {
           a: 1,
           b: 2,
           c: 3,
       }

   (there might be more options) (also applies to lists and function
   parameters)
-  named/anonyoumus functions

   -  There are three ways of defining a function

      1. var a = function() {}
      2. function b() {}
      3. var a = function b() {}

   -  tl;dr: The first version is least confusing and should be
      preferred.
   -  Further reading

      -
http://stackoverflow.com/questions/336859/var-functionname-function-vs-function-functionname
      -  http://kangax.github.io/nfe/#expr-vs-decl

TypeScript
----------

-  imports at top

   -  separate external and internal
   -  only import from lower level

-  allow nested types ``Foo<Bar<Baz>>`` (how deep?)
-  when to use ``() => x`` instead of ``function () {}``
-  how strictly enforce types?

Angular
-------

-  prefere isolated scope in directives
-  where is direct DOM manipulation/jQuery allowed?
-  dependency injection

   -  always use ``['$q', function($q) {…}]`` style

-  which syntax do we use for directives?

   -  ``<adh-foo>``
   -  ``<div adh-foo>``
   -  ``<x-adh-foo>``
   -  ``<adh:foo>``
   -  ``<div class="adh-foo">``

-  compability

   -  https://docs.angularjs.org/guide/ie

-  do not use $ in your variable names (leave it to angular)
-  prefix

   -  one or multiple?
   -  adh? a3?

Template
~~~~~~~~

-  prefere ``{{…}}`` over ``ngBind`` (except for root template)
-  valid XHTML5
-  when to apply which classes (should be in balance with CSS
   Guidelines)

   -  apply classes w/o a specific need/by default?


