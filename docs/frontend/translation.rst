Translation
===========

Whenever you want to do translation of Adhocracy content, we strongly
encorage you to do the following steps:

1) if necessary: mark the content you need to translate as translatable,
2) extract translatable strings for a translation session,
3) translate the strings in `transifex`_,
4) if necessary: update the change_german_salutation script.

1. Markup Translatable Strings
------------------------------

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


2. String Extraction
--------------------

angular-translate does not provide a script to extract translatable
strings.  So we hacked our own:

-  ``bin/ad_extract_messages`` will output
   a list of all translatable strings in the current git subtree.

   .. NOTE: It relies on the ``TR__`` prefix to find translatable
      strings in TypeScript code.

-  You can pipe the output into
   ``bin/ad_merge_messages`` to update the
   JSON files.  It takes two parameters: The package name and a filename
   prefix, e.g.::

      bin/ad_merge_messages adhocracy_frontend core

So in order to update the translation files in the "foo" package, you
can use the following command::

   cd src/foo/
   ../../bin/ad_extract_messages | ../../bin/ad_merge_messages foo foo

.. NOTE:: Both scripts are not of good quality and may not cover all
   edge-cases.


3. Translation with Transifex
-----------------------------

We generally use `transifex`_ for translation. Note that new strings
in the code are not automatically displayed in transifex, and
updates in transifex are not instantly reflected in either the code
or any running platform.

Before you push local changes to transifex, please make sure that you
will not overwrite any translations on transifex. This can be done in
several ways, one of which is the following. Assuming you want to update
the project called foo::

   $ cd src/foo/
   $ tx pull -a --force
   $ git cola

In git cola, for each line you can decide on the newer version.

Then, in order to push changes from the foo project code to transifex,
the transifex-client can be used like this::

   $ cd src/foo/
   $ tx push -a

In order to pull changes from transifex into the foo project's code,
the transifex-client can be used like this::

   $ cd src/foo/
   $ tx pull -a

.. NOTE:: The configuration for transifex-client is stored in
   ``src/{package_name}/.tx/config``.

.. WARNING:: Transifex requires us to specify a "source language"
   (currently English). This has the benefit that translators do not
   need to handle technical strings. But it also has several
   disadvantages:

   -  The source language can not be translated on transifex.

   -  All translations will be lost when the string in the source
      language is changed.

   -  Downloaded translation files will contain all keys. Any key
      that does not have a translation will have the translation from
      the source language as a value.

   An alternative could be to have a fake source language that simply
   has the technical strings themselves as translations and an exotic
   locale.


4. German Du/Sie
----------------

Adhocracy is currently used mostly in Germany, i.e. in German language.
Unfortunately, there are two variants of German, a formal (Sie) and an
informal (Du) one.

All translations should use the informal variant. When necessary, we
use the script ``bin/change_german_salutation`` to convert informal
translations to formal ones.  Note that you will need to extend that
script whenever the translation changes. The common workflow for this
is: Iteratively run the script, check the output and add new rules
until everything is fine.


.. _angular-translate: https://angular-translate.github.io
.. _transifex: https://www.transifex.com/liqd/adhocracy3/
