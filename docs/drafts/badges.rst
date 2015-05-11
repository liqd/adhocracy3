Badges
======

This is a summary of the "badge concept" user story. The concepts are
not yet implemented in Adhocracy 3.

Adhocracy 2 knows a variety of badges and similar entities. The aim is
to streamline these entities into more consistent or possibly independent
concepts in Adhocracy 3. Some aspects shall not be implemented in A3.

This document can be replaced once the concepts are ready in A3.


Badge features in Adhocracy 2
-----------------------------

The various badges, categories and tags can be categorized as the
following:


Allowed targets
    What can be badged?


Locality
    Do badges exist globally or locally only?

Exclusivity
    Can only one badge out of a certain group be assigned to a target
    object?

Hierarchy
    Can badges be structured hierarchically?

Dedicated pages
    Does this badge have a dedicated page?


Create permission
    Who may create badges / choose available badges in a given context?

Assign permission
    Who may assign badges to targets?

View permission
    Who may view badges?


Color
    If shown as normal badge, what color should it have?

Icon
    If shown as thumbnail, which icon should be shown?

Visibility
    Should it be shown at all in listings?


Impact
    Effect on mixed list sortings

Implicit user role
    If a user has this badged, which additional role should she have?
    (we should drop this)

Voteable
    Allow users to vote whether the assignment applies (tags in
    Adhocracy 1)

Behaviour
    Assign a certain behaviour to a badge (research project at HHU)


Badges, categories and tags in A2
---------------------------------

Some remarkable aspects of badge-like entities in A2:


Default
    -   Non-exclusive
    -   Non-hierarchical
    -   No dedicated pages
    -   No icon
    -   No image
    -   Can be created and assigned by moderators
    -   All badges can exist globally and additonally per instance

Categories
    -   Can be assigned by normal users
    -   Exclusive
    -   Hierarchical
    -   Have dedicated pages
    -   Have an image

Thumbnail badges
    -   Have an icon

User badges
    -   Can have optional user role assignment

Tags
    -   Can be created and assigned by normal users
    -   Have no color


Requirements for badges in A3
-----------------------------

(this is incomplete)

-   Allow to define which badges can be assigned to a certain
    resource with which rules (see features above).

-   It must be possible to freely define multiple available badge groups.

-   Allow to define badges globally and locally. It should be possible
    to restrict and extend the available badges locally.

-   NTH: Badges can be connected through a common taxonoy, i.e. if a
    local process wants to call a badge `Umweltpolitik` it can be
    connected to a global badge `Umwelt`.

-   All badges shall be indexed and can be used in pool queries.


Example
+++++++

Some proposal resource might be badged as the following:

-   Badge group `decision_state`:

        - available badges "beschlossen", "abgelehnt"
        - exclusive
        - creatable by admins (not really necessary, because hardcoded)
        - assignable by moderators

-   Badge group `topic`:

        - creatable by moderators
        - assignable by users
        - hierarchical
        - non-exclusive
