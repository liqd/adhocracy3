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

-  We prefer conventions set by 3rd party tools (e.g. `tslint`_) over our
   own preferences.
-  We try to be consistend with other guidelines from the adhocracy3
   project

General JavaScript
------------------

We follow most rules proposed by tslint (see tslint config for details).
However, there are some rules we want to adhere to that can not (yet) be
checked with tslint.

-  Use `strict mode`_ everywhere

   -  There seem to be multiple issues with strict mode and Typescript
      -  http://typescript.codeplex.com/workitem/2003
      -  http://typescript.codeplex.com/workitem/2176

-  No implicit boolean conversions: ``if (typeof x === "undefined")`` instead
   of ``if (!x)``

-  Chaining is to be preferred.

   -  If chain elements are many lines long, it is ok to avoid
      chaining.  In this case, if chaining is used, newlines and
      comments between chain elements are encouraged.

   -  Layout: Each function (also the first one) starts a new line.  The
      first line (without a ``.``) is indented at n+0, all functions at
      n+1 (4 spaces deeper).

-  Each new identfier has its own ``var``. (rationale: ``git diff`` / conflicts)

-  Do not align your code. Use the following indentation rules instead
   (single-line option is always allowed if reasonably short.):

   -  objects::

         foo = {
             a: 1,
             boeifj: 2,
             cfhe: 3}

   -  lists::

         foo = [
             138,
             281128]

   -  function definitions::

          var foo(a : number) : number => a + 1;

          var foo = (arg : number) : void => {
              return;
          }

          var foo = (
              arg: number,
              otherarg: Class) : void =>
          {
              return;
          }

-  Do not use named functions. Assign anonymous functions to variables instead.
   This is less confusing. `Further reading
   <http://kangax.github.io/nfe/#expr-vs-decl>`_

FIXME:

-  when to return promises (this point may need to go to another place in this doc?)

   - only when needed directly, or when expected to be needed in e.g. subclass.

-  If you need an alias for ``this``, always use ``self`` (as in knockout).
   (``_this`` is used by typescript in compiled code and is disallowed
   in typescript source in e.g. class instance methods.)

   if more than one nested self is needed, re-assign outer ``self``\ s
   locally.

TypeScript
----------

-  imports at top

   -  standard libs first (if such a thing ever exists), then external
      modules, then a3-internal modules.

   -  only import from lower level.  ("lower level" does not mean file
      directory hierarchy, but something to be clarified.  this rule
      is to be re-evaluated at some point.)

-  nested types are allowed up to 2 levels (``Foo<Bar<Baz>>``).  1
   level is to be preferred where possible.

-  Type the functions, not the variables they are assigned to.

-  TypeScript has its own lambda syntax::

      var fn = (x) => x.attr;

-  Use ``Array<type>`` rather than ``type[]``
-  use ``() => x`` instead of ``function() {}``.
   rationale: ``() => ...`` has two benefits over ``function() {}``:

     1. lexical scoping: ``=>``-style functions are wrapped with a ``var
        _this = this;``, all occurrances of ``this`` in the body are
        replaced by ``_this``.  this is a deviation from javascript
        syntax, but leads to much clearer code, since the meaning of
        ``this`` is appearent from the context of the function definition,
        not the function call.

     2. ``() => 3 + 4`` is shorter than ``function() { return 3 + 4; }``

     3. using two syntaxes for the same concept is bad.

   possible reasons against using ``=>``-notation::

         -  javascript developers will be confused.  (objection: this
            is good, because they need to understand that there is a
            difference between the two, namely lexical scoping.)

         -  it deviates from javascript.  (objection: this is good,
            because dynamic scoping is inherently hard to understand
            and debug.)

         -  vim does not support ``=>`` syntax highlighting.
            (objection: there is a blogpost that provides a typescript
            mode for vim:
            http://blogs.msdn.com/b/interoperability/archive/2012/10/01/sublime-text-vi-emacs-typescript-enabled.aspx.
            if that does not solve this issue, a rule should be easy
            enough to add.)

-  how strictly to enforce types?

Angular
-------

-  prefer isolated scope in directives and pass in variables
   explicitly.

-  direct DOM manipulation/jQuery is only allowed inside directives.

-  dependency injection

   -  always use ``["$q", function($q) {…}]`` style

-  compatibility

   -  https://docs.angularjs.org/guide/ie

-  do not use ``$`` in your variable names (leave it to angular).

-  prefix

   - directives: 'adh.*' for all directives declared in a3.  (in the
     future, this prefix may be split up in several ones, making
     refactoring necessary.  Client-specific prefices may be added
     without the need for refactoring.)

   - service registration: '"adhHttp"'.  (services must be implemented
     so that they don't care if they are registered under another
     name.)

   - service module import: 'import Http = require("Adhocracy/Services/Http");'.
     rationale: When using service modules, the fact that they provide
     services is obvious.

Template
~~~~~~~~

-  which syntax do we use for directives?

   -  ``<adh:foo>`` or ``<x-adh-foo>``?

   -  what about element/directive attributes?

-  valid XHTML5: we use an html checker.  (which one?  does that work
   statically, or do we have to check dynamically rendered dom trees?)

-  prefer ``{{…}}`` over ``ngBind`` (except for root template).
   FIXME: check that ``{{…}}`` is never rendered temporarily!

-  when to apply which classes (should be in balance with CSS
   Guidelines)

   -  apply classes w/o a specific need/by default?

Documentation
~~~~~~~~~~~~~

-  Use `jsdoc`_-style comments in your code.
   -  Currently, no tool seems to be available to include JSDoc
      comments in sphinx.
   -  `Typescript has only limited JSDoc support
      <http://typescript.codeplex.com/workitem/504>`_


.. _strict mode: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions_and_function_scope/Strict_mode
.. _tslint: https://github.com/palantir/tslint
.. _jsdoc: http://usejsdoc.org/
