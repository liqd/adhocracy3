Git Guidelines
==============

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

  In order to do that, you may want to use helper tools such as
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

Terminology
~~~~~~~~~~~

If branch A is branched from branch B, then B is called A's *base
branch*.

A branch is called *published* if it has been pushed to a repository
that is accessed by more than one user.  Usually, this means the
project-specific central upstream repository, but a branch is also
considered published if one developer has pushed changes to another
developer's laptop.)


Branch types
~~~~~~~~~~~~

Branch naming follows a pattern that makes it easier to process
branch lists automatically.  The pattern consists of year (``YYYY``),
month (``MM``), a developer name shortcut (``DEV``), keywords (small
letter words), and descriptive free text (``[-a-z]+``).

The following branch types exist:

Story branches (``YYYY-MM-story-[-a-z]+``)
   For each user story, there is a story branch that must be based on
   ``master``.  Story branches may sprout personalized or volatile
   branches (see below).

Fix branches (``YYYY-MM-fix-[-a-z]+``)
   For each bug on the story board, a fix branch is created.  It must
   be based on ``master``.

Personalized branches (``YYYY-MM-DEV-[-a-z]+``)
   Developers create personalized branches in order to work on tasks.
   Personalized branches may be based anywhere.  It is **not** allowed
   to ``push --force`` a personalized branch.

Volatile branches (``YYYY-MM-_DEV-[-a-z]+``)
   Personalized branches with ``push --force`` option.  The developer
   must announce that this branch may change arbitrarily by adding an
   underscore mark before the developer name shortcut in the branch
   name.  Volatile branches may be based anywhere.


Finding branch points
~~~~~~~~~~~~~~~~~~~~~

For the processes defined in this document, it is interesting to find
the points in the repository where a branch branched off other
branches in the past.  We call these points *branch points*.

Note that the information at which point a branch branched off its
direct base branch is `not maintained by git
<http://stackoverflow.com/questions/17581026/branch-length-where-does-a-branch-start-in-git>`_.
This does not make the question of the direct base branch any less
meaningful, but it makes it tricky to answer.

If the base branch is ``master``, then you can get a reference to
the branch point of the current branch like this::

    export BRANCHPOINT=`git rev-list HEAD ^master --topo-order | tail -n 1`~1
    git show $BRANCHPOINT

(``git show-branch`` yields more relevant data, but in a less
machine-readable form.)


Rebase and +n-branch logic
~~~~~~~~~~~~~~~~~~~~~~~~~~

To keep the code history clean, a personalized branch may be rebased
before it is merged into its base.  (Volatile branches may
always be rebased, because there is no guarantee that they behave in
any way as branches should.)

Rebasing has two advantages:

- You can move your branch to the HEAD of the base branch as an
  alternative to merging.  This way you keep a near-linear commit
  history;

- with the ``-i`` option, rebasing allows to re-order and clean up
  individual commits, and thus make the life of the reviewer (and
  anyone else looking at the history) easier.

In order to avoid that ``rebase`` changes repository state
destructively (instead of just adding additional commits), the rebase
must happen according to *+n-branch logic*::

    # (complete work on branch, say, 2014-05-mf-bleep based on, say, master)
    # (make sure that upstream is set to origin/2014-05-mf-bleep)
    git push -v
    git checkout -b 2014-05-mf-bleep+1
    git rebase master
    git push -v origin 2014-05-mf-bleep+1

Remarks:

- the un-rebased branch has no +n suffix, the first rebase has '+1',
  the second '+2' and so on.

- if you call rebase with argument ``-i``, you can do a lot of
  rebase magic (squashing and dropping and reordering and all that).
  This feature is quite self-explanatory -- just try it!  [FIXME:
  there was an oddity when you are in the editor and want to cancel.
  @nidi, can you fill that in here?  i think you've explained this
  to me once.]

- if you call ``git rebase -i $BRANCHPOINT``,
  you can do rebase magic without actually changing the branch
  point.


Dos and Don'ts
~~~~~~~~~~~~~~

1. ``push --force`` is forbidden.  The only exception are volatile
   branches.

2. ``rebase`` is generally forbidden on published branches.
   Exceptions: ``rebase`` is allowed in volatile branches; ``rebase``
   with +n-branch logic is allowed in personalized branches and
   allowed-but-discouraged in story branches.

3. Always use ``git merge`` with ``--no-ff`` when merging a branch
   into its base branch.

   (When merging the base branch into a story or personalized branch
   to benefit from code recently added elsewhere, fast-forward is
   usually not possible since the histories of two merged branches
   have diverged.  ``--no-ff`` usually does not apply in this case.)

   If you want to make ``--no-ff`` the default (you can still
   explicitly enable it with ``--ff``)::

     git config --global merge.ff true

4. Merging ancestor branches into a current branch is ok.  This makes
   it feasible to keep up to date with changes in a base branch in
   long-living story or personalized branches.  The merge commit will be eliminated
   if the current branch is rebased on the ancestor branch HEAD at any
   point in time after the merge.

5. Fixes to trivial issues may be committed by a developer directly to
   master without branching.  The commit must be at least mentioned to
   one more developer, who must check whether the issue qualifies as
   trivial and the commit is sound.
