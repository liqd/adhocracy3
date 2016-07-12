CSS
===

Preface
-------

In recent years, methodologies like
`OOCSS <https://github.com/stubbornella/oocss/wiki>`_,
`SMACSS <http://smacss.com>`_,
`BEM <http://bem.info/method/definitions/>`_,
`SUIT <https://github.com/suitcss/suit/>`_,
`Pattern driven Design <http://www.patterndrivendesign.com/>`_, and
`Atomic Design <http://patternlab.io/about.html>`_ have shifted the
focus from designing pages to designing systems.

The best known application of this is probably `bootstrap
<https://getbootstrap.com/>`_. But as one of bootstraps main developers
said: You are encouraged to `build your own bootstrap
<https://speakerdeck.com/mdo/build-your-own-bootstrap>`_.  This document
describes the details of how we create our own design system for
adhocracy3.

Common Terminology
------------------

To work together it is important to share a common language.
Unfortunately, JavaScript programmers, CSS developers, and graphic
designers sometimes have very different angles on the same things.
The following terminology is therefore based on the tried and tested
systems mentioned above.

Base Styling
++++++++++++

Base styling is the styling that applies to HTML elements when no
additional classes are added. It sets the prevailing mood for a product.
This involves general *text styling* as well as *links*, *headings*, and
*input boxes*.

Layout
++++++

The layout defines the position of elements on a page. It is typically
based on a grid system.

Components
++++++++++

There are many synonyms for this in the different methodologies:
Object (OOCSS), module (Smacss), block (BEM), atom/molecule/organism
(Atomic Design), or pattern (pattern driven design).

Components are independent of their context and can be reused throughout
the UI. A typical component is a *button* or a *login dialog*. The rule
of thumb is: If in doubt, it is a component.

Element
+++++++

An element is a part of a component that can not be used on its own. A
typical example is a menu item (always part of a menu component).

States
++++++

Components may have different *states* (e.g. *hover*, *active*, or
*hidden*). States are always bound to specific components (e.g. there is
no general *active* state).

Modifiers
+++++++++

Components can have derived, modified versions. For example, there could
be a button and a *call-to-action* button. In this case, call-to-action
would be a modifier. (If you know about object oriented programming:
this is similar to a subclass).

Modifiers are very similar to states because both modify a component.
The rule of thumb to distinguish the two is that whereas the state of a
component usually changes over time, modifiers don't.

Variables
+++++++++

A variable can be used to define a value in a single place and then use
it wherever we want. We could for example define the variable
``primary-color`` and use it throughout the UI. This allows us to change
that color in a single place which makes theming easy.

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

   -  must mark any components, states, modifiers, and variables in
      wireframes.

   -  may request new components, states, … from the team.

      -  They must decide whether the new component, state, … should be
         part of core or theme.

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

   -  must provide designs for all components, states, …

   -  They must provide all necessary information and files as soon as
      possible (to avoid delays, preliminary dummy files may be
      provided). This includes:

      -  fonts
      -  icons
      -  background images/logos
      -  FIXME: define file formats, image resolution, …

-  CSS developers …

   -  must provide a living style guide (breakdown of all existing
      components, states, …).
   -  must report implementation issues as soon as possible.
   -  must implement features as requested.

CSS, HTML, and JavaScript
-------------------------

This section describes the collaboration between CSS developers and
JavaScript programmers.

-  JavaScript does not set any CSS on elements. Instead it adds/removes
   states.
-  Some CSS testing should be done in browser tests, i.e. CSS and JavaScript
   developers should work together on this.

Selectors
+++++++++

This section describes which selectors must be used for different
types. All classes are lowercase and hyphen-separated.

-  component: class (no prefix)
-  layout: class (prefix: ``l-``)
-  element: class (prefix: component name)
-  state: pseudo-class, attribute, class (prefix: ``is-`` or ``has-``)
-  modifier: class (prefix: ``m-``)

CSS Specifics
-------------

Preprocessor
++++++++++++

CSS preprocessors help a great deal in writing modular, maintainable CSS
code by offering features like variables, imports, nesting, and mixins.
Major contenders are `Sass <http://sass-lang.com/>`_,
`Less <http://lesscss.org/>`_ and
`Stylus <http://learnboost.github.io/stylus/>`_. We had good expiriences
with Sass so we will stick with it. CSS developers must read the `Sass
documentation <http://sass-lang.com/documentation/file.SASS_REFERENCE.html>`_.


Documentation and Style Guide
+++++++++++++++++++++++++++++

A style guide in (web)design is an overview of all available colors,
fonts, and components used in a product. In the context of CSS it can be
generated from source code comments. In some way this is similar to
doctests in python.

There is a long `list of style guide
generators <http://vinspee.me/style-guide-guide/>`_. We chose to use
`hologram <http://trulia.github.io/hologram/>`_ because it integrates
well with our existing CSS tools.

Hologram is automatically installed when running buildout. You can use
``bin/buildout install styleguide`` to build the style guide to
``docs/styleguide/``.

All variables, components, base styles, states, and modifiers must be
documented (including HTML examples). Variables also need documentation
and examples. As these do not expose selectors which could be used in
examples it might be necessary to create ``styleguide-*``-classes.

Common Terminology Considerations
+++++++++++++++++++++++++++++++++

These are some CSS/SCSS specific thoughts on the common language terms
defined above.

Modules
~~~~~~~

A module is a SCSS file. Each component should have its own module
including its states and modifiers. Several base styles may be
included in a single module if they are closely related. The same goes
for layout, variables, and mixins.

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

States and Modifiers
~~~~~~~~~~~~~~~~~~~~

States and modifiers are always specific to a component. They have to be
defined within the scope of the component.

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

Formatting
++++++++++

We have a pre-commit hook with most of the `sass-lint linters
<https://github.com/sasstools/sass-lint/tree/master/docs/rules>`_
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
   -  distances relative to element font-size ``em``
   -  else: ``rem``
   -  for thin lines or in the context of images, ``px`` may be used to
      avoid low-quality rescaling

-  font-size: variable, ``rem``, ``%``
-  0 length: no unit
-  line-height: no unit, ``em``, ``rem``

   -  see `explanation by Eric Meyer
      <http://meyerweb.com/eric/thoughts/2006/02/08/unitless-line-heights/>`_.

-  color: keyword, short hex, long hex, ``rgba``, ``hsla``
-  generally prefer variables to keywords to numeric values

   -  keywords are easier to apprehend when skipping through the code

.. Note::

   For all ``rem`` units the ``rem()`` mixin should be used, e.g.::

      @include rem(margin, 10px 5px);
      @include rem(margin-bottom, 2rem);
      @include rem(border, 3px solid $color-function-positive);

   This automatically calculates ``rem`` units with a ``px`` fallback
   for older browsers.

Accessibility
+++++++++++++

-  Be careful about hiding things (``hidden`` vs. ``visually-hidden``)
   (see http://a11yproject.com/posts/how-to-hide-content/).
-  Use `fluid and responsive
   design <http://alistapart.com/article/responsive-web-design>`_
   (relative units like ``%``, ``em``, and ``rem``).
-  Prefer to define foreground and background colors in the same spot.
   Use `color-contrast
   <https://xi.github.io/sass-planifolia/#contrast>`_ by
   sass-planifolia.
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

One of the most complicated issues in CSS in general is whether styles
should change depending on context. On the one hand we talk about
*responsive design*, on the other, components should be decoupled (`Law
of Demeter <http://en.wikipedia.org/wiki/Law_Of_Demeter>`_) to keep the
code maintainable.

It is important to understand that there are two different kinds of
context awareness involved here:

1. Elements inherit CSS rules from their context (e.g. ``font-family``
   is shared across the whole document if set on the ``html`` element).
2. CSS code can apply additional styling to an element if it appears in
   a specific context (e.g. ``#sidebar h2 {color: red;}``).

Inheritance is hard to avoid and does little damage. So we should
embrace it.

I am not so sure about child selectors:
`OOCSS container <https://github.com/stubbornella/oocss/wiki#separate-container-and-content>`_
and `SMACSS subclassing <http://smacss.com/book/type-module#subclassing>`_ both
recommend to avoid them. Still it is a powerful feature. This is still
an open question.
