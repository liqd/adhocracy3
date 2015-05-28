Frontend Routing
================

As Adhocracy 3 is a single page application, the routing is done in the
frontend.  Unfortunately, the obvious choice `angular-route`_ does not
meet our requirements so we wrote our own router.  This document gives
a brief overview over the routing system.

Basics
------

Adhocracy 3 consists of a backend with a rest API and a frontend with
a server part and a client part (JavaScript).  The frontend server
serves static files for the most part.  The frontend client is a complex
application that manages most of the routing.

Routing in Adhocracy 3 relies on angular's ``$location`` service which
in turn uses the browser's `history API`_ (or a fallback if that is not
available).  This allows us to change the URL from JavaScript code
without triggering a browser redirect.

Server
------

The routing is done on the client.  However, the server still needs to
serve the frontend code on all valid URLs.  The existing rules already
cover quite a lot.  If you want to add another rule (basically if you
want to add another *area*, see below) you need to edit
``src/adhocracy_frontend/adhocracy_frontend/__init__.py`` or the
corresponding file in a customization package.  Simply add a line like
this to :py:func:`includeme`::

    add_frontend_route(config, name, rule)

where ``name`` is the name of this route and ``rule`` is a rule that the
URL will have to match.  See `pyramid add_route documentation`_ for
further details.

Top Level State
---------------

The ``adhTopLevelState`` service provides the infrastructure for
routing in the Adhocracy 3 frontend.  It manages an internal flat object
called the *state* and syncs it with the URL.  So whenever the URL
changes, the state is updated and vice versa.  The service provides an
interface to get, set and watch the state.

The service also defines a template that is rendered by the ``adhView``
directive.

In some respects, ``adhTopLevelState`` is similar to `angular-route`_
but much more flexible.

Areas
+++++

The actual work of syncing URL and state as well as defining the
template is not done by ``adhTopLevelState`` itself but by so called
*areas*.  This allows us to have very different routing methods in
different areas.

The current area is selected by the first part of the URL path.  So if
the URL is ``http://example.com/foo/bar/1?key=value``, the area is
``foo``.

Each area defines a function :js:func:`route` to convert the URL to a
state object, :js:func:`reverse` to convert a state object to an URL,
and a template.

Currently, we use some simple areas for login related functionality, one
area for embedding and (the most important) one for resources.

Resource Area
+++++++++++++

The most important area is the resource area.  URLs in this area are
directly derived from backend paths.  If a resource has the path
``/some/path`` in the backend, the corresponding route in the frontend
would be ``/r/some/path``.

Much like ``adhTopLevelState``, the resource area only provides an
infrastructure.  You need to configure what the state should be based on
*resource type*, *view*, *process type* and *embed context*.

While the resource type can be deduced from the path, view, process type
and embed context are new concepts. *Process type* and *embed context*
will be discussed later in this document.

*Views* allow to have multiple routes to a single resource.  So while
``/r/some/path`` might point to a detail view of the resource,
``/r/some/path/@edit`` might point to a form where the resource
can be edited.  Note that the view is prefixed with an ``@``.

Spaces
++++++

``adhTopLevelState`` can store multiple state objects at the same time.
These are called *spaces*.  They allow to easily switch between multiple
application states.

This is backed by the ``adhSpace`` directive which will only show its
contents if the passed key is that of the current space.  This way not
only the top level state object, but also the complete DOM is preserved.

Currently, only the resource area makes use of spaces.  It divides its
pages into a "user" and a "content" space.

Process
-------

While the previous concepts were frontend specific, *processes* also
exist in the backend.  A process contains a resource subtree and defines
roles and permissions for that subtree.

In the frontend it also defines which template should be used.  The
directive ``adhProcessView`` is used to render that template.  It is
currently used in the resource area's content space.

Embed Context
-------------

For a general discussion of embedding, see :ref:`Embedding`.

When entering adhocracy through the embed area, an embed context is
defined. This changes how the resource area behaves. For example there
might be a different template or different routes.

Conclusion
----------

So here is a rough overview of what happens when I enter
``/r/some/path`` into my browser address bar:

1.  The server serves an HTML bootstrap page.
2.  ``adhTopLevelState`` notices a change to the URL and starts
    processing it.  From the first part of the URL (``/r/``) it knows
    that it has to use the resource area.
3.  The resource area converts the URL to a flat state object.
    This object contains information about space and process type.
4.  ``adhView`` renders the area template.
5.  The ``adhSpace`` directive for the content space renders its
    contents, while all other spaces are being hidden.
6.  ``adhProcessView`` renders the process template.

Note that everything except for the first step also happens when I click
on a link within Adhocracy.

.. _angular-route: https://docs.angularjs.org/api/ngRoute
.. _history API: https://developer.mozilla.org/en-US/docs/Web/API/History
.. _pyramid add_route documentation: http://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.add_route
