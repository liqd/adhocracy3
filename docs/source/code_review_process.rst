Code Review Process
===================


Preface
-------

This document describes a light-weight code review process that can be
used with git alone and no other tools.


Status of this document
-----------------------

This document should be read as request for comments (RFC).  It will
be used for a trial period of two sprints (starting from 2014-06-10);
in the sprint starting on 2014-07-21, a decision will be made on which
parts of this document will remain valid.


Requirements
------------

This section is a (hopefully complete) list of all requirements of the
a3 development team as of 2014-06-02, in arbitrary order.  As some of
the requirements are inconsistent, the following sections necessarily
constitute a compromise (and not necessarily the optimum in any
metric).

- low-footprint, trivial to adopt.

- no need to adjust work habits to yet another new application
  software / UI.

- offline use (no need having IP connectivity while working).

- git repo contains all review history in the resp. branches (to the
  extend those branches have not been deleted).

- allow for synchronous review (talk the branch through together on
  the same physical display).

- allow for asynchronous review (pass comments and little fractional
  changes back and forth between reviewer and reviewee through
  something as convenient as email or a web page).

- passing a branch back and forth between reviewer and reviewee
  during the review process should be trivial.

- the reviewer can make changes (e.g. small typos) herself, not only
  ask the reviewee to do them.  (all changes by the reviewer of
  course need to be double-checked by the reviewee.)

- comments can be attached to
  - the branch
  - lines in the full diff
  - individual commits
  - lines in commit diffs

- review comments can contain links into web / other code locations /
  other commits / ...

- review comments and code should be separated, e.g. in a file called
  ``REVIEW.txt`` in the root directory of the repository that can be
  easily removed before the merge.

- review comments should be contained in the code as comments,
  probably in a special mark-up form that can be pruned automatically
  before the merge.

- github-style pull requests

- email notifications for

  - branches ready for review

  - passing a branch back and forth between reviewer and reviewee.

  emails should contain context and links.

- allow to rebase a branch (or a clone of the branch) during the
  review process.


Tool Candidates
---------------

Should we decide in the future to use software on top of git, this is
an incomplete list of options:

- `bugseverwhere`_
- `gerrit`_
- `gitissues`_
- `reviewboard`_
- `phabricator`_


Git Conventions
---------------


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


Code Review
-----------

Code review happens on personalized branches.  Merging a story branch
into master happens right after the merge of the last necessary
personalized branch, so no review process is needed there.

The merge of a story branch should be done by two persons, but this is
not a strong rule.

All changes and comments that the reviewer makes are either made
directly in the code (see Section 'Markup language' below), or in a
file called ``REVIEW.txt`` located in the working copy root.
Reviewer and reviewee should agree on which option is preferred for
what.


Synchronous Process
~~~~~~~~~~~~~~~~~~~

0. The author has completed a personalized branch for review.

1. The author chooses a reviewer and contacts her in person or by
   any means preferred by both.

   All documentation of the pull request must be contained in the
   commit log (short and long commit messages).  Any documentation to
   the PR as a whole is appended to the commit log in an empty commit
   (``git commit --allow-empty``).

2. The reviewer checks out the branch to be reviewed, and makes
   changes and comments in the working copy.

3. Reviewer and author go through the comments in person.

4. Once all comments and changes have been agreed on, one or more
   additional commits are made by the author or by author and reviewer
   in pair programming mode.

5. The branch is merged into its base branch.


Asynchronous Process
~~~~~~~~~~~~~~~~~~~~

0. The author has completed a personalized branch for review.

1. *(create pull request)* (PR) The author sends an email to a3-dev with
   subject ``[PR] bloo (audience)``, where ``bloo`` is the name of
   the branch and ``audience`` is a description of possible reviewers
   (e.g. names or the name of the subsystem).

   All documentation of the pull request must be contained in the
   commit log (see synchronous process).  The commit log (or the last
   commit) may be contained in the email body.

2. *(assign pull request)* A reviewer sends a response to the PR on
   a3-dev with subject ``Re: [PR] ...`` and an optional message in the
   body (e.g. "I'll do the review tomorrow").  If several reviewers
   respond simultaneously, they resolve the conflict outside this
   process.

3. The reviewer checks out the branch to be reviewed, makes any
   changes and comments in the working copy, and adds them to the
   branch in one or more commits.  The short commit messages must
   start with ``[R]`` for review.

4. *(merge)* If there are no more review comments or changes, the
   reviewer merges the branch into its base.  The branch must not be
   merged until all review comments are resolved.

5. *(re-assign)* If there are changes, the reviewer sends a response
   to the PR to a3-dev.  Body may be empty
   or contain the commit log.  At this point, reviewer and author
   change roles, and the author becomes the reviewee.  Proceed at
   step 3.


Recipes
~~~~~~~

As above, first do something like::

    git checkout branch-to-be-reviewed
    export BRANCHPOINT=...  (see above)

To see which files have changed::

    git diff $BRANCHPOINT --stat

If file paths are shortened you might want to specify a width like this::

    git diff $BRANCHPOINT --stat=3000

To see all changes in a branch in one diff::

    git diff $BRANCHPOINT

To see all changes to an individual file::

    git diff $BRANCHPOINT -- <path>

To see all changes, organised by commits and enriched with commit
messages::

    git whatchanged -p $BRANCHPOINT..

To get a richer interface you can pipe the output of all of these
commands into `tig`_


Markup language
~~~~~~~~~~~~~~~

The file ``REVIEW.txt`` may contain any free text.  (A format for what is
in there may emerge in the future; there may also be tools in the
future to process it.)  For example it may be useful to add commit
lines that can be interpreted by tig (see
https://github.com/jonas/tig/issues/299).

The reviewer may make any changes to the code, including comments, in
the hope that the author will like them and keep them in the final
branch HEAD.

In addition, the reviewer may make specially marked comments that the
author needs to process.  These comments must match the regex::

    ^# REVIEW: .*

Depending on the language of the file under review, the ``#`` must be
replaced by the respective comment lexeme (``#`` for python and yaml,
``//`` for javascript, typescript and SCSS, ``<!--`` for html (with
the extra ``-->`` at the end), ``..`` for rst, and so on).

Further lines may be added after this.  Those just need to match
``^# .*`` or corresponding.  Note the space in both the first and
all following lines.

Debates may emerge as author and reviewer realize they disagree.  In
that case, the comment answering a ``REVIEW`` comment may start after
an empty line with::

    ^# REVIEW[mf]: .*

where ``mf`` is the developer shortcut of the developer that adds the
comment.  While this information may also be available from ``git blame``
it is convenient to have it right there.

During the review phase, ``REVIEW`` comments may either be removed
manually or transformed into helpful comments to be imported into the
base branch.


Dos and Don'ts
~~~~~~~~~~~~~~

A branch must not be merged as long as ``REVIEW`` comments remain.

``FIXMEs`` are discouraged in master.  For now, they are allowed, but we
should find a more fancy bug tracking approach.  (redmine?)

FIXME[cs]: Personally, I mostly use FIXME for "this works as is, but it
is a hack/inelegant/inefficient, so if we could find a better solution that
would be great", NOT for bugs. For bugs and things that really need to be
resolved to make the code function as it's supposed to, I use TODO and
ensure that all TODOs are indeed handled and deleted before merging into
master.

FIXME[mf]: ``git notes --help`` may be relevant, but I haven't looked at
it yet.

FIXME[nd]: we want the commit hook to work on staged copy, not working
copy.  (where should we move this point?  i don't think it belongs
here.)

FIXME[mf]: line numbers!  we want code line numbers everywhere!  can git
do line numbers in every line in diff?

FIXME[tb]: following things might be useful additions:

- what should/must be done before creating a pull request
     - only one feature per pull request
         - only include changes that are really needed; do refactoring
           in a separate pull request
         - small fixes and library updates should be done in or near master,
           not inside of larger feature branches. This allows everyone to
           profit sooner. In cases where the fix/update would have been done
           in multiple branches, this also avoids merge conflicts.
     - be prepared to explain every single change.


.. _bugseverwhere: http://bugseverywhere.org/
.. _gerrit: https://code.google.com/p/gerrit/
.. _gitissues: https://github.com/duplys/git-issues
.. _reviewboard: http://www.reviewboard.org/
.. _phabricator: https://secure.phabricator.com/book/phabricator/article/introduction/
.. _tig: https://github.com/jonas/tig
