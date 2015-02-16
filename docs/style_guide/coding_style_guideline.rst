Coding style guideline
======================

Testing
-------

* 100% test coverage (must)
* Test driven development with acceptance/functional, integration und unit test (should)

  * testing guideline: http://pyramid.readthedocs.org/en/latest/narr/testing.html
  * unit test examples substanced code, http://www.diveintopython.net/unit_testing/
  * testdriven concept: http://www.c2.com/cgi/wiki?TestDrivenDevelopment)


Git commits
-----------

Git commits serve different purposes:

* Allow reviewers to quickly go through your changes.
* Help developers in the future to understand the intention of your change
  using ``git blame``.
* Use the break of writing a commit message as an opportunity to reflect on
  what you have just coded.
* Backup what you did and allow reverting to an earlier state, if necessary.

These goals may be in conflict with other goals (such as "have more
time for writing tests and code"), and sometimes even with each other
("small commits" vs. "test suite always works").  Therefore, this
section does not contain any strict rules, but suggestions.  The
reader is encouraged to decide in which contexts they make sense.  (In
particular, "should" is not the RFC-all-caps "SHOULD", but something
to consider.)

Suggestions:

* Aim at making small commits containing only one semantic change.

  In order to that, you may want to use helper tools such as
  `tig <https://redmine.liqd.net/issues/1184>`_,
  `git-cola <https://git-cola.github.io/>`_ or plain ``git add --interactive``
  or ``git add --patch``, allowing for easy line-by-line staging. Interactive
  rebasing (``git rebase -i``) may help with cleaning up history in retrospect,
  i.e. splitting / combining / reordering commits. Be aware of not pushing
  published non-volatile branches (as described in :doc:`code_review_process`).

* The test suite should run through successfully on every commit. Test coverage
  doesn't necessarily need to be 100% on each commit, as some developers may
  want to split commits in functional code and testing code and write the
  latter later. Of course writing the tests first is preferred.

* For the actual commit message, we follow the rules, which are codified
  `as an example <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_
  by tpope:

    Capitalized, short (50 chars or less) summary

    More detailed explanatory text, if necessary.  Wrap it to about 72
    characters or so.  In some contexts, the first line is treated as the
    subject of an email and the rest of the text as the body.  The blank
    line separating the summary from the body is critical (unless you omit
    the body entirely); tools like rebase can get confused if you run the
    two together.

    Write your commit message in the imperative: "Fix bug" and not "Fixed bug"
    or "Fixes bug."  This convention matches up with commit messages generated
    by commands like git merge and git revert.

    Further paragraphs come after blank lines.

    1. Bullet points are okay, too

    2. Typically a hyphen or asterisk is used for the bullet, preceded by a
       single space, with blank lines in between, but conventions vary here

    3. Use a hanging indent

* Referring to other commits can be done by using their hash ID.  Be aware
  that the hash ID changes on rebase.


Descriptive summary prefix keywords are encouraged, but there is no
strict rule as to which keywords exist and where to use them.  Here is
a list of options:

* Refactor (optionaly followed by a commit hash)

* Fixup (optionally followed by a commit hash to squash this one into;
  defaults to previous commit)::

    Fixup a93bhd34: typo

* Gardening (for changes that do not significantly change the meaning
  or structure of the code, such as style guide fixes)

Note that there's already standard messages for commits created by git
(Revert "...") and conventions for review commits (``[R] prefix``) as
described in the :doc:`code_review_process`.


Git branches
------------

Use and naming of git branches is explained in the code review process
document.


Python
------

Code formatting
+++++++++++++++

* 4 spaces instead of tabs (must)
* no trailing white space (must)

* `pep8 <http://legacy.python.org/dev/peps/pep-0008/>`_ (must)
* pyflakes (must)
* pylint (should)
* mcabe (should)

* Advances String Formatting `pep3101 <http://legacy.python.org/dev/peps/pep-3101/>`_ (must)

* Single Quotes for strings except for docstrings (must)

Docstring formatting
++++++++++++++++++++

* pep257 (must, bei tests und zope.Interface classes should)
* python 3 type annotation (must) according to
  https://pypi.python.org/pypi/sphinx_typesafe
* javadoc-style parameter descriptions, see
  http://sphinx-doc.org/domains.html#info-field-lists (should)
* example::

    def methodx(self, a: dict, flag=False) -> str:
        """Do something.

        :param a: description for a
        :param flag: description for flag
        :return: something special
        :raise ValueError: if a is invalid
        """


Imports
+++++++

* one import per line
* don't use * to import everything from a module
* don't use relative import paths
* dont catch ``ImportError`` to detect wheter a package is available or not, as
  it might hide circular import errors. Instead use
  ``pkgresources.getdistribution`` and catch ``DistributionNotFound``.
  (http://do3.cc/blog/2010/08/20/do-not-catch-import-errors,-use-pkg_resources/)

Javascript
----------

See :doc:`js_guidelines`.

CSS/Compass
-----------

See :doc:`css_guidelines`.

Restructured text
+++++++++++++++++

* 4 spaces instead of tabs (must)
* no trailing white space (must)
* Headline hierarchy: ===== ----- +++++ ~~~~~~~ ****** (must)
