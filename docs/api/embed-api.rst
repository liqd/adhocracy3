Embed-API
=========

The general idea consists of two parts: the SDK javascript code, which has to
be loaded once, and widget markers in the DOM. On initialization, the widget
markers are replaced by iframes, which show the actual content.


SDK snippet
-----------

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
--------------

A widget is defined by

- One embeddable angular directive (presentation)
- Optionally a locale
- Multiple directive parameters

Constraints:

- Syntax should exist for both HTML5 (`data`- parameters) and HTML4


Example (current HTML5 syntax)::

    <div class="adhocracy_marker" data-widget="proposal-workbench" data-content="/proposal"></div>


What happens internally
-----------------------

Say we use the following marker::

    <div class="adhocracy_marker" data-widget="proposal-workbench" data-content="/proposal"></div>

This will be converted to the following URL for the iframe::

    //example.com/embed/proposal-workbench?content=/proposal

The template inside of that iframe will look roughly like this::

    <adh-proposal-workbench data-content="/proposal"></adh-proposal-workbench>


Allowing a directive to be embedded
-----------------------------------

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
------------------------

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

    <adh-my-directive data-variable1="1" data-variable2="2" ></adh-my-directive

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
