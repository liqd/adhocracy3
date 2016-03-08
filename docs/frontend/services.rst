Services
========

This section gives a brief introduction to the most important services.

adhConfig
  Provides access to the configuration. Basically identical with
  ``/config.json`` on the frontend.

adhHttp
  All HTTP communication should go through this services. Apart from
  caching it also contains abstractions for some API features such as
  :ref:`batch requests <batch-requests>` or :ref:`OPTIONS requests
  <meta-api-options>`.

adhPermissions
  This service wraps ``adhHttp.options()`` and updates the result
  whenever the resource path changes.

adhTopLevelState
  Basic infrastructure for routing. You will need to use this service if
  you want to know things about the current route, e.g. which process
  you are in.

adhResourceArea
  Implements some more concrete aspects for routing. You will mostly use
  this to configure routes for individual resource types.
