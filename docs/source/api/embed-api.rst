Embed-API
=========

The general idea consists of two parts: the SDK javascript code, which has to
be loaded once, and widget markers in the DOM. On initialization, the widget
markers are replaced by iframes, which show the actual content.


SDK snippet
-----------

- Bootstraps everything, initializes widgets
- Select Adhocracy version to be used
- Opens `adhocracy` namespace
- Resizes widgets on the fly

Example::

    <script type="text/javascript" src="https://adhocracy.lan/frontend_static/js/AdhocracySDK.js"></script>
    <script type="text/javascript">
        adhocracy.init('http://adhocracy.lan', function(adhocracy) {
            adhocracy.embed('#adhocracy_marker');
            // Not part of embed snipped. Only here for testing.
            document.getElementsByClassName("adhocracy-embed")[0].id = "adhocracy-iframe";
        });
    </script>


Widget markers
--------------

A widget is defined by

- One angular directive (presentation)
- Multiple directive parameters, e.g.

  - One or multiple resources (content)
  - Initial widget state? (e.g. initial list sorting)
  - Other widget parameters? (e.g. specify subwidgets)


Constraints:

- Different HTML5 (`data`- parameters) and HTML4 syntax (different)


Example (current HTML5 syntax)::

    <div id="adhocracy_marker" data-widget="proposal-workbench" data-content="/proposal"></div>
