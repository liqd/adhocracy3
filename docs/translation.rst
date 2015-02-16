Frontend translation
====================

Markup translatable strings
---------------------------

For translations in the frontend we use `angular-translate`_.  It
offers several ways of marking a string as translatable, but we
mainly use the ``translate`` filter in templates::

   <a href="#">{{ "TR__LOGIN" | translate }}</a>
   <a href="#">{{ "TR__USERS_PROPOSALS" | translate:{name: adhUser.name} }}</a>

In few cases it is not possible to do translation in the template.
In these cases you can also use the ``$translate`` service. Note that
this service returns a promise::

   $translate("TR__LOGIN").then((translated) => {
       ...
   });

In our code we do not use actual human language. Instead, we use
technical strings (uppercase, with underscores, prefixed with ``TR__``).


String extraction
-----------------

angular-translate does not provide a script to extract translatable
strings.  So we hacked our own:

-  ``adhocracy_frontend/scripts/extract_messages.sh`` will output
   a list of all translatable strings.

   .. NOTE: It relies on the ``TR__`` prefix to find translatable
      strings in TypeScript code.

-  You can pipe the output into
   ``adhocracy_frontend/scripts/merge_messages.py`` to update the
   files in ``adhocracy_frontend/static/i18n/``.

.. NOTE:: Both scripts are not of good quality and may not cover all
   edge-cases.


Translation
-----------

Translators can use `transifex`_ for translation. Note that changes in
transifex are not instantly reflected in neither the code nor any
running platform. In order to pull changes from transifex into the code,
the transifex-client can be used::

   $ cd src/adhocracy_frontend/
   $ tx pull -a

.. NOTE:: The configuration for transifex-client is stored in
   ``src/adhocracy_frontend/.tx/config``.

.. NOTE:: transifex-client is currently not compatible with python3.4
   and can therefore not be installed in the usual way.  If you need
   it, just install it via::

      pip install --user transifex-client


Missing Features
----------------

-  There is currently no mechanism to translate stuff from the backend
   (e.g. mail templates)


.. _angular-translate: https://angular-translate.github.io
.. _transifex: https://www.transifex.com/projects/p/adhocracy3mercator/
