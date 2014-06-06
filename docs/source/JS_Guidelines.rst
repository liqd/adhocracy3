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
-  strict comparisons (``===`` and not ``==``)
-  no implicit boolean conversions: ``if (typeof x === "undefined")`` instead of ``if (!x)``
-  semicolons: always.  (tslint and strict tell you the specifics)
-  4 space indentation

TODO:

-  tsLint configuration

   -  https://github.com/palantir/tslint

-  chaining:

   -  chaining is to be preferred.

   -  if chain elements are many lines long, it is ok to avoid
      chaining.  in this case, if chaining is used, newlines and
      comments between chain elements are encouraged.

   -  layout: each '.' (also the first one) starts a new line.  the
      first line (without a '.') is indented at n+0, all '.' lines at
      n+1 (4 spaces deeper).

-  single or mutliple ``var``\ s  rule: each new identfier has its own 'var'.  (rationale: git diff / conflicts)

-  when to return promises (this point may need to go to another place in this doc?)

   - only when needed directly, or when expected to be needed in e.g. subclass.

-  consistent alias for ``this``: ``self`` (as in knockout).
   (``_this`` is used by typescript in compiled code and is disallowed
   in typescript source in e.g. class instance methods.)

   if more than one nested self is needed, re-assign outer selves
   locally.

-  alignment.  general rule is "no alignment".  details::

       foo = {
           a: 1,
           boeifj: 2,
           cfhe: 3}

       foo = [
           138,
           281128]

   (single-line option is always allowed if reasonably short.)

   function definitions::

       var foo = (
           arg: number,
           otherarg: Class) =>
       {
           return;
       }

       var foo = (arg: number) => {
           return;
       }

   (single-line argument declarations *enforce* opening ``{`` in same
   line.)

-  named/anonyoumus functions

   -  There are three ways of defining a function

      1. var a = function() {}
      2. function b() {}            -- not allowed
      3. var a = function b() {}        -- insane

   -  tl;dr: The first version is least confusing and should be
      preferred.
   -  Further reading

      - http://stackoverflow.com/questions/336859/var-functionname-function-vs-function-functionname
      - http://kangax.github.io/nfe/#expr-vs-decl

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

   reasons against using ``=>``-notation::

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

-  prefer isolated scope in directives.  (exception: ``ngRepeat``)

-  where is direct DOM manipulation/jQuery allowed?  -- only inside directives.

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
   check that ``{{…}}`` is never rendered temporarily!

-  when to apply which classes (should be in balance with CSS
   Guidelines)

   -  apply classes w/o a specific need/by default?
