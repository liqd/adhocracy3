Embedding
=========

Adhocracy 3 is designed to be "embed first". This means that it will
usually not be used on its own, but embedded in some website, e.g. a
content management system (CMS).  But it should also be possible to
embed individual widgets.

Terms
-----

The following terms are used in the context of embedding:

Host
    The website where adhocracy is embedded.

Widget
    A piece of adhocracy that can be embedded on its own.  Some
    functionality (e.g. registration) will require the user to switch
    to the *platform*.  See also :doc:`css_guidelines`.

Frontend URL
    This is where the actual adhocracy frontend is available.  Users are
    not supposed to interact with this directly.  Instead, the frontend
    should be embedded somewhere.

Platform URL
    This is where the full adhocracy is available (as opposed to a
    widget).  The term *platform* also refers to the complete set of
    functionality and navigation that sets it apart from a mere widget.

Canonical URL
    Content can show up in different places (i.e. with different URLs),
    namely at the frontend URL, the platform URL and embedded in many
    more places.  The canonical URL is the *default* URL. In most cases
    (but not in all!), it will point to the platform.  See also `RFC6596
    <https://tools.ietf.org/html/rfc6596>`_.


General notes
-------------

-   Accout activation (after registration) and password reset require
    that the backend sends a URL to the user via email.  So the backend
    needs to know canonical URLs for that.

-   If a feature is not available in an embedded widget, all aspects of
    that widget that rely on that feature need to be modified.  For
    example, whenever a user is referenced, we include a link to their
    profile page.  If profile pages are not available in an embedded
    widget, these links either need to be removed or point to the
    platform instead.


Embed-API
---------

The general idea consists of two parts: the SDK javascript code, which has to
be loaded once, and widget markers in the DOM. On initialization, the widget
markers are replaced by iframes, which show the actual content.


SDK snippet
+++++++++++

This is our JavaScript code that runs in the host page.  It was
carefully written to not interfere with the hosts own JavaScript code.

- Bootstraps everything, initializes widgets
- Selects Adhocracy version to be used
- Opens `adhocracy` namespace
- Resizes widgets on the fly

Example::

    <script type="text/javascript" src="https://adhocracy.lan/static/js/AdhocracySDK.js"></script>
    <script type="text/javascript">
        adhocracy.init('http://adhocracy.lan', function(adhocracy) {
            adhocracy.embed('.adhocracy_marker');
        });
    </script>

One or more markers can appear anywhere in the document::

    <div class="adhocracy_marker"
         data-widget="document-workbench">
    </div>
    <div class="adhocracy_marker"
         data-widget="paragraph-version-detail"
         data-locale="en"
         data-ref="..." data-viewmode="display">
    </div>


Widget markers
++++++++++++++

A widget is defined by

- One embeddable angular directive (presentation)
- Optionally a locale
- Multiple directive parameters

Constraints:

- Syntax should exist for both HTML5 (`data`- parameters) and HTML4


Example (current HTML5 syntax)::

    <div class="adhocracy_marker" data-widget="proposal-workbench" data-content="/proposal"></div>


Special parameters
~~~~~~~~~~~~~~~~~~

-   the special widget ``"plain"`` will embed the full platform instead
    of a single widget::

        <div class="adhocracy_marker" data-widget="plain"></div>

-   ``autoresize`` will control whether the iframe will automatically be
    resized to fit its contents.  Defaults to ``true``.  It is
    recommended to set this to ``false`` if the embedded widget contains
    moving columns::

        <div class="adhocracy_marker" data-widget="plain" data-autoresize="false"></div>

-   ``locale`` can be used to set a locale.

-   ``autourl``: If set to ``true``, the URL of the embedded adhocracy
    will be appended (and constantly updated) to the host URL via ``#!``.
    This is only possible once per host page for obvious reasons.

-   ``initial-url`` will set the initial URL (i.e. path, query and
    anchor) for the embedded platform if widget is ``"plain"``.


What happens internally
+++++++++++++++++++++++

Say we use the following marker::

    <div class="adhocracy_marker" data-widget="proposal-workbench" data-content="/proposal"></div>

This will be converted to the following URL for the iframe::

    //example.com/embed/proposal-workbench?content=/proposal

The template inside of that iframe will look roughly like this::

    <adh-proposal-workbench data-content="/proposal"></adh-proposal-workbench>


Allowing a directive to be embedded
+++++++++++++++++++++++++++++++++++

Not every directive is allowed to be embedded.  You need to register it
with the embed provider::

    import AdhEmbed = require("../Embed/Embed");

    export var myDirective = () => {
        // your directive's code
    };


    export var moduleName = "adhMyModule";

    export var register = (angular) => {
        angular
            .module(moduleName, [
                AdhEmbed.moduleName
            ])
            .config(["adhEmbedProvider", (adhEmbedProvider : AdhEmbed.Provider) => {
                adhEmbedProvider.registerEmbeddableDirectives(["my-directive"]);
            }])
            .directive("adhMyDirective", [myDirective]);
    };


Embed Widget for testing
++++++++++++++++++++++++

As a side effect, the embed API can be used to develop and test
functionalities of frontend widgets in an isolated way.

Say you have registered a directive as described in the previous
section.  Now you can see your widget under::

    /embed/my-directive

Maybe you would also like to add data to your directive using
attributes. As there is no surrounding scope to your directive, this
needs to be mocked. You can do that by appending some GET parameters to
your URL::

    /embed/my-directive?variable1=1&variable2=2

The HTML element that is added to the embed page will look like this::

    <adh-my-directive data-variable1="1" data-variable2="2" ></adh-my-directive>

In your directive you can now for example use this like this::

    export var myDirective = () => {
        return {
            scope: {
                variable1: "@",
                variable2: "@"
            },
            // more code
        };
    };
