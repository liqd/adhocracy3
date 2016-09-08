Concepts
========

resource
--------

Anything that exists in adhocracy is a resource: A proposal, a
comment, but also users or individual rates.

resource type
-------------

Think of a resource type as a blueprint, and a resource as
the actual building you build by following the blueprint. Example:
The proposal "Better food in the cafeteria" would have the type
``adhocracy_core.resources.proposal.IProposal``.  Note that all
resources of the same type have the same sheets,
so there might be a lot of similar types with slightly different
sheets (e.g. a simple proposal, a proposal with a budget, a
proposal with a geographical location, ...).

sheet
-----

Sheets are the features of resources. A
proposal may for example have the sheet
``adhocracy_core.sheets.title.ITitle`` that allows it to have a
title and the sheet ``adhocracy_core.sheets.comment.ICommentable``
that allows it to be commented on. A resource is really not much
more than the sum of its sheets.

backend / frontend
------------------

The backend is the part of the software that stores the data.  The
frontend on the other hand is in charge of showing the data to
users.  Having a clear separation between these makes development
simpler and theoretically allows to have more than one frontend,
e.g. a website and a mobile app.

core / customization
--------------------

Not all projects implemented with adhocracy are the same. That
is why it is very easy to customize it for each individual
project. The shared functionality is called "core" while the
special code is called "customization".

process
-------

A process resource represents a participation process.
There are very different kinds of these. Idea Collections, where
users can enter proposals and get feedback, and giving feedback on
prepared documents, are probaly the most common ones.

permissions
-----------

What a user is permitted to do depends on their role.  The roles a
user has often depend on the context. Example: Amelia (user) may
be the creator (role) of one proposal (context) and therefore
permitted to edit it (permission). Proposals that she hasn't
created, she may not edit, but she may comment on them.

workflow states
---------------

Participation processes typically have multiple phases: For example, you
may want to first publish an announcement, then have the actual
participation for some time, and display the results once that is over.
This is possible by using workflows that can have different states.

Workflows can be used with processes, but also with any other kind of
resource. An important feature of workflows is that you can change the
permissions for each role based on the state.
