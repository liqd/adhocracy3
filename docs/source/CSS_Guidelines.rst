CSS Guidelines
==============

Preface
-------

This document describes the CSS development process in the context of
Adhocracy 3. However, it is not specific to Adhocracy 3 and can be
applied in any project which needs CSS code.

-  If you are a CSS developer you should read the whole document.
-  Everyone concerned with the frontend should read `Goals`_ and
   `Common Terminology`_.
-  UI designers and graphic designers should also read `CSS and Design`_.
-  JavaScript programmers should also read `CSS, HTML, and JavaScript`_.

Goals
-----

There are several goals we want to accomplish by the processes and rules
described in this document:

1. We want the collaboration within the project to work well. This
   includes clear responsibilities and a common language in which we can
   communicate. The collaboration should still work if new people come
   into the project or the size of the team changes dramatically.

2. We want our code to run smoothly with very few bugs and little
   maintenance work. It should be easy to add new parts or replace existing
   ones. It should be easy to derive customized themes.  Using derived themes
   after an upgrade of the core CSS code should be easy.

3. We want to deliver a great product with a flawless and accessible
   user experience (UX).

Common Terminology
------------------

To work together it is important to share a common language.
Unfortunately, JavaScript programmers, CSS developers, and graphic
designers sometimes have very different angles on the same things.

With the following terms I try to find (and name) common grounds. This
terminology is largely based on existing systems like
`OOCSS <https://github.com/stubbornella/oocss/wiki>`_,
`SMACSS <http://smacss.com>`_ and
`BEM <http://bem.info/method/definitions/>`_. The basic idea is to apply
concepts known from object oriented programming (OOP) to CSS code. The
descriptions are written so that non-programmers should be able to grasp
them easily.

We think of elements in the user interface (UI) as *objects*. A typical
object might be a link, button or a list. It is important to understand
the difference between a specific object (e.g. "the safe button in the
login view") and its *class* ("button").

We distinguish several types of objects. There are also the related
concepts *state*, *modifier*, *variable*, *mixin*, and *adjustment*.

Base Objects
++++++++++++

When HTML elements are used without any special modifications, they are called
base objects. The basic styling of these elements sets the prevailing mood for
a product. This involves general *text styling* as well as *links*, *headings*,
and *input boxes*.

Widget Objects
++++++++++++++

Widgets are the most common objects. They can be reused throughout the UI. A
typical widget is a *button* or a *login dialog*. While base objects are
limited to existing HTML elements we can define our own widgets.

Page
++++

FIXME: definition

A page does not only include all objects that are rendered to screen. It also
contains some meta data like title, description and image that might be used by
third part services (facebook, google, …) to render a preview.

Installation
++++++++++++

An installation includes a complete installment of the product. Apart from all
pages it also includes some global meta data like title, URL and favicon.

Layout Objects
++++++++++++++

The layout defines the basic structure of a page. Typical layout objects
are *header*, *main*, *aside*, and *footer*. Of most layout objects there
is only a single instance on a page (e.g. only one header and footer).

The styling of layout objects must only define position and size. Any
other styling must be applied to objects inside of the them.

Element Objects
+++++++++++++++

We call objects within widgets *elements* of that widget. An element may
be a widget itself. If an element appears in more than one widget it must
be a widget.

States
++++++

Widgets or base objects may have one or more *states* (e.g. *hover*,
*active*, or *hidden*). States may either be applicable to any object
(*hidden*) or only to specific objects (*hover*, *active*).

Modifiers
+++++++++

Widgets can have derived, modified versions. For example, there could
be a button and a *call-to-action* button. In this case, call-to-action
would be a modifier. In terms of OOP, a modifier is similar to a
subclass.

This concept is very similar to that of states because both modify an
object.  The rule of thumb to distinguish the two is that whereas the
state of a widget usually changes over time, its modifiers don't.

Variables
+++++++++

A variable can be used to define a value in a single place and then use
it wherever we want. We could for example define the variable
``primary-color`` and use it throughout the UI. This would allow us to
later change that color in a single place instead of change the complete
code wich of course improves consistency and makes theming easy.

Mixins
++++++

Some styling is not specific to an object but instead is shared by many
different objects. This is called a *mixin* because it can simply be
added to an object. A typical example would be a gradient: You may want
to use the same type of gradient, but with different colors and on
different objects.

Mixins are similar to variables in that they store something that can be
used anywhere in the UI. But whereas variables store single values, mixins
can store complex sets of rules.

Adjustments
+++++++++++

Any code that can not be reused is called an *adjustment*. Adjustments
should be avoided wherever possible.

Core, Themes, and Default Theme
+++++++++++++++++++++++++++++++

The project may create multiple CSS-themes for the software. All themes
share a common core. Themes can theoretically overwrite every aspect of
the core. Since overwrites come at a run-time cost for the browser, they
should be kept at a minimum. To make this possible it is advised to keep
the core small and flexible.

Keeping the core small may conflict with a good UX in the default case.
To avoid that, a default theme is included to separate the
default UX from the core.

CSS and Design
--------------

This section describes the collaboration between UI designers, graphic
designers, and frontend developers. All the rules apply to core, default theme,
and any additional themes.

-  UI designers …

   -  must mark any objects, states, modifiers, variables, mixins, and
      adjustments in wireframes.

   -  may request new objects, states, … from the team.

      -  They must decide whether the new object, state, … should be part
         of core or theme.

      -  They must provide semantically rich names for all new features.
         (e.g. "light-foreground" instead of "grey"; see Robert C Martin,
         Clean Code, Chapter 2)

      -  Variables are mandatory for all colors and font sizes.

   -  must provide the contents of a view in a linearized and thus
      prioritized sequence in addition to the layout structure. This is
      needed e.g. for screen readers (assistive technology for the
      blind) and web crawlers.

-  Graphic designers …

   -  must provide values for all variables.

   -  must provide designs for all objects, states, …

   -  They must provide all necessary information and files as soon as
      possible (to avoid delays, preliminary dummy files may be
      provided). This includes:

      -  fonts
      -  icons
      -  background images/logos
      -  FIXME: define file formats, image resolution, …

-  CSS developers …

   -  must provide a living style guide (breakdown of all existing objects,
      states, …).
   -  must report implementation issues as soon as possible.
   -  must implement features as requested.

CSS, HTML, and JavaScript
-------------------------

This section describes the collaboration between CSS developers and
JavaScript programmers.

-  JavaScript does not set any CSS on elements. Instead it adds/removes
   states.
-  There is a mechanism to track classes used by JavaScript code. It
   should help in tracking which classes are actually used and which are
   dead code. See the CSS typescript module
   (``/src/adhocracy/adhocracy/frontend/static/js/Adhocracy/Css.ts``)
   for more information.
-  Some CSS testing should be done in browser tests, i.e. CSS and JavaScript
   developers should work together on this.

Selectors
+++++++++

This section describes which selectors must be used for different
object types. All classes are lowercase and hyphen-separated.

-  widget: class (no prefix)
-  base: tag
-  layout: class (prefix: ``l-``)
-  element: class (prefix: widget name)
-  state: pseudo-class, attribute, class (prefix: ``is-`` or ``has-``)
-  modifier: class (prefix: ``m-``)
-  mixin: none (handled internally in CSS)

CSS Specifics
-------------

Framework
+++++++++

CSS frameworks like `bootstrap <http://getbootstrap.com/>`_ and
`foundation <http://foundation.zurb.com>`_ have become popular in recent
years. However we decided to not use any of them because all of those
frameworks do more than we wanted them to do. For example they all
include button layouts which collide with our own. This has led to UI bugs
in the past.

While we do not use a full framework we try to be somewhat compatible in
both code structure and wording. It may be possible to reuse code from
those frameworks as modules in our own code.

Preprocessor
++++++++++++

CSS preprocessors help a great deal in writing modular, maintainable CSS
code by offering features like variables, imports, nesting, and mixins.
Major contenders are `Sass <http://sass-lang.com/>`_,
`Less <http://lesscss.org/>`_ and
`Stylus <http://learnboost.github.io/stylus/>`_. We had good expiriences
with Sass so we will stick with it. CSS developers must read the `Sass
documentation <http://sass-lang.com/documentation/file.SASS_REFERENCE.html>`_.

We also use `Compass <compass-style.org>`_ — a library providing many useful mixins
and functions for Sass.

There are many more interesting projects in that ecosystem. Currently, we are
not using any of these. But we might be using some in the future.

-  https://github.com/Team-Sass/breakpoint
-  https://github.com/simko-io/animated.sass
-  http://susy.oddbird.net/

-  http://www.sitepoint.com/my-favorite-sass-tools/
-  http://hackingui.com/front-end/10-best-scss-utilities/


Documentation and Style Guide
+++++++++++++++++++++++++++++

A style guide in (web)design is an overview of all available colors,
fonts, and widgets (more generally: objects) used in a product. In the
context of CSS it can be generated from source code comments. In some
way this is similar to doctests in python.

There is a long `list of style guide
generators <http://vinspee.me/style-guide-guide/>`_. We chose to use
`hologram <http://trulia.github.io/hologram/>`_ because it integrates
well with our existing CSS tools.

Hologram is automatically installed when running buildout. You can use
``bin/buildout install styleguide`` to build the style guide to
``docs/styleguide/``.

All variables, widgets, base objects, states, and modifiers must be
documented (including HTML examples). Variables and mixins also need
documentation and examples. As these do not expose selectors which could
be used in examples it might be necessary to create
``styleguide-*``-classes. Layout and adjustments must have some kind
of documentation though it might be hard to give HTML examples for
those.

Common Terminology Considerations
+++++++++++++++++++++++++++++++++

These are some CSS/SCSS specific thoughts on the common language terms
defined above.

Modules
~~~~~~~

A module is a SCSS file. Each widget should have its own module
including its states and modifiers. Several base objects may be
included in a single module if they are closely related. The same goes
for layout, variables, and mixins. Adjustments must go into separate
modules.

It is recommended to use (modified) modules from 3rd party projects such
as `bootstrap <https://github.com/twbs/bootstrap/tree/master/less>`_ or
`foundation <https://github.com/zurb/foundation/tree/master/scss/foundation/components>`_.

All SCSS files not to be compiled on their own must begin with
an underscore (``_``). They must be structured into folders reflecting
the common terminology: ``widgets``, ``layout``, ``base``, ``states``
(only global states), ``variables``, ``mixins``. Further structure may
be added as needed.

Variables
~~~~~~~~~

-  Do not add variable definitions like
   ``$color-default: blue !default;`` to your modules because this may
   hide errors. Define all global variables in a central place instead.
-  You should use local variables if you need to use the same value
   multiple times. Still in most cases it is possible to avoid these
   situations by grouping selectors or similar.

   Bad::

       $padding: 2em;

       .box1 {
           padding: $padding;
       }
       .box2 {
           padding: $padding;
       }

   Worse::

       .box1 {
           padding: 2em;
       }
       .box2 {
           padding: 2em;
       }

   Good::

       .box1,
       .box2 {
           padding: 2em;
       }

Modifiers
~~~~~~~~~

Modifiers are always specific to a widget. They have to be defined
within the scope of the widget.

Mixins
~~~~~~

There are two ways to implement mixins in Sass: ``@mixin`` and
``@extend``. There are basically three differences:

-  a ``@mixin``, once defined, can be used everywhere. ``@extend``\ s
   are are compiled into selector groups, which may not be possible
   depending on what you are trying to do.
-  ``@mixin`` allows parameters and content blocks.
-  ``@extend`` may produce more efficient (less redundant) CSS.

There is no rule about which one is preferred. As ``@mixin`` is simpler to use
you might by tempted to use it exclusively. Always stop and also consider
``@extend``.

Theming
~~~~~~~

Each theme replicates the directory structure of core. Sass must be
configured so that both theme and core are in the import path. This
allows to import all modules from core while making it easy to overwrite
a module by adding a corresponding file to the theme.

Formatting
++++++++++

We have a pre-commit hook with most of the `scss-lint linters
<https://github.com/causes/scss-lint/blob/master/lib/scss_lint/linter/README.md>`_
with their default settings, except for the following modifications:

-  4 space indentation.

-  Include leading zero.

-  Double quotes instead of single quotes.

-  Comma-separated selectors need not be on their own lines. Still this is a
   must for composite selectors.

-  A strict property sort order is not enforced. Still the properties should
   appear in roughly the following order:

   -  ``content`` (only used on pseudo-selectors)
   -  box -- ``display``, ``float``, ``position``, ``left``, ``top``,
   -  ``border``
      ``height``, ``width``, ``margin``, ``padding``
   -  text -- ``font-family``, ``font-size``, ``line-height``,
      ``text-transform``, ``letter-spacing``, …
   -  color -- ``background``, ``color``
   -  other

The following additional rules apply:

-  similar to `pep8 <http://legacy.python.org/dev/peps/pep-0008/>`_

   -  only one property per line;
   -  no trailing whitespace
   -  two spaces between rule and comment, one after comment initialiser
      (good: ``color: white;  // foo``; bad: ``color: white; //foo``)
   -  prefer lines < 80 chars if possible
   -  spaces around binary operators

-  opening bracket at the end of the last selector line
-  closing bracket in its own line
-  avoid vendor specific prefixes/hacks in your code. You may however
   use mixins that create compatible code for exactly one thing (e.g.
   ``border-radius`` mixin by compass)

Units
+++++

This gives an order of preference for the units that must be used with
different types of values starting from preferred.

-  length:

   -  layout: ``%``
   -  else: ``em``
   -  not sure about ``rem`` because of compatibility
   -  in the context of images, ``px`` may be used to avoid low-quality
      rescaling

-  font-size: keyword, ``%``, ``px``

   -  outside of variable definitions only variables and ``%`` must be
      used

-  0 length: no unit
-  line-height: no unit, ``em``, ``px``
-  color: keyword, short hex, long hex, ``rgba``, ``hsla``
-  generally prefer variables to keywords to numeric values

   -  keywords are easier to apprehend when skipping through the code

Accessibility
+++++++++++++

-  Be careful about hiding things (``hidden`` vs. ``visually-hidden``)
   (see http://a11yproject.com/posts/how-to-hide-content/).
-  Use `fluid and responsive
   design <http://alistapart.com/article/responsive-web-design>`_
   (relative units like ``%`` and ``em``).
-  Prefer to define foreground and background colors in the same spot.
   Use
   `color-contrast <http://beta.compass-style.org/reference/compass/utilities/color/contrast/>`_
   by compass.
-  While no support for IE < 9 is planned, do not introduce
   incapabilities where not needed (robust).

Icons
+++++

You should avoid using pixel images as they are inflexible in size. If
possible, prefer iconfonts. You can use `Font
Custom <http://fontcustom.com>`_ to easily generate an icon font from
SVG files.

Context
+++++++

One of the most complicated issues in CSS in general is whether objects
should change depending on context. On the one hand we talk about
*responsive design*, on the other, objects should be decoupled (`Law of
Demeter <http://en.wikipedia.org/wiki/Law_Of_Demeter>`_) to keep the
code maintainable.

It is important to understand that there are two different kinds of
context awareness involved here:

1. Objects inherit CSS rules from their context (e.g. ``font-family`` is
   shared across the whole document if set on the ``html`` element).
2. CSS code can apply additional styling to an object if it appears in a
   specific context (e.g. ``#sidebar h2 {color: red;}``).

Inheritance is hard to avoid and does little damage. So we should
embrace it.

I am not so sure about child selectors:
`OOCSS <https://github.com/stubbornella/oocss/wiki#separate-container-and-content>`_
and `SMACSS <http://smacss.com/book/type-module#subclassing>`_ both
recommend to avoid them. Still it is a powerful feature. This is still
an open question.
