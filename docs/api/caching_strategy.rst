Caching strategy
================

Caching is realized on different levels:

- Caching of static resources (javascript, html, css, images)
- Caching of content resources


Caching static resources
------------------------

The rough idea is to cache static resources (javascript, HTML, CSS, images)
forever by adding a timestamp or checksum to a query string to each static
resource file, which changes each time the file has changed. This allows both
browser and proxy (e.g. varnish) caching.

Two mechanisms are used for static file caching at the moment:

- HTML template files are joined together as a Javascript module, which can
  be used to prefill the angular template cache.

- JS and CSS files are cached through `pyramid_cachebust` and custom code in
  `adhocracy_frontend/__init__.py`. This adds a query string with a timestamp
  (frontend webserver start time) to each resource to be loaded.

  Pyramid 1.6 will contain native cachebusting functionality, so some things
  might be implemented differently then.

In the future, we may want to add individual checksums for each file instead of
one timestamp for all to allow more fine-grained caching and decrease load
after server restarts. However this would require a more sophisticated
RequireJS setup, or concatenation of all Javascript files.


Caching content resources
-------------------------

Both backend and frontend cache content resources. Both caches are manually
invalidated, triggered by the backend.


Backend resource caching (Varnish)
++++++++++++++++++++++++++++++++++

To be described.


Frontend resource caching
+++++++++++++++++++++++++

To be described.
