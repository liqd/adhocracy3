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

-  allow chaining?  [YES! ~~mf]

   -  where it might be useful:

      -  promises (``.then()``)
      -  angular registration

   -  if chaining is allowed: how should it be indented?
      [each '.' starts a new line.  the first line (without a '.') is indented at n+0, all '.' lines at n+4  ~~mf]

-  single or mutliple ``var``\ s  [multiple vars are disallowed.  each new identfier has its own 'var'.  ~~mf]
-  when to return promises

   -  wherever it might someday be useful
   -  only where absolutely needed
   [neither, but where it makes sense semantically.  not sure if we need a rule for that?  ~~mf]

-  consistent alias for ``this``  [``_this`` is used by typescript in compiled code and is disallowed in typescript source in some places.  ``xthis``?  ~~mf]
-  alignment::

       foo = {a: 1,
              b: 2,
              c: 3}

   or::

       foo = { a: 1,
               b: 2,
               c: 3 }

   or::

       foo = { a: 1
             , b: 2
             , c: 3
             }

   or::

       foo = {
           a: 1,
           b: 2,
           c: 3,
       }

   (there might be more options) (also applies to lists and function
   parameters)
   [i'm willing to settle for a compromise with what our IDEs are capable of indenting automatically.  ~~mf]
-  named/anonyoumus functions

   -  There are three ways of defining a function

      1. var a = function() {}
      2. function b() {}
      3. var a = function b() {}

   -  tl;dr: The first version is least confusing and should be
      preferred.
   -  Further reading

      - http://stackoverflow.com/questions/336859/var-functionname-function-vs-function-functionname
      - http://kangax.github.io/nfe/#expr-vs-decl

TypeScript
----------

-  imports at top

   -  all internal identifiers must be defined after all external identifiers
   -  only import from lower level

-  allow nested types ``Foo<Bar<Baz>>`` (how deep?)
-  when to use ``() => x`` instead of ``function () {}``

   [``() => {}`` has the benefit over ``function() {}`` that its
   'this' is a bit more sane.  also, i prefer the syntax from an
   asthetic point of view.  ~~mf]

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
   -  ``<x-adh-foo>``  (this is good because it's xHTML-compliant)
   -  ``<data-adh-foo>``  (this is good because it's HTML5-compliant)
   -  ``<adh:foo>``
   -  ``<div class="adh-foo">``  no (i think this is only for compatibility with very old browsers)

-  compability

   -  https://docs.angularjs.org/guide/ie

-  do not use $ in your variable names (leave it to angular)
-  prefix

   -  one or multiple?
   -  adh? a3?

   [don't we want to use this code in a4 as well?  :)  what about liq?  ~~mf]

Template
~~~~~~~~

-  prefere ``{{…}}`` over ``ngBind`` (except for root template)
-  valid XHTML5
-  when to apply which classes (should be in balance with CSS
   Guidelines)

   -  apply classes w/o a specific need/by default?


