Permission system:
------------------

Principals:
...........

groups (set of users):

   - Authenticated (all authenticated users, standard group)
   - Everyone (all authenticated and anonymous users, standard group)
   - gods (initial custom group, no permission checks)
   - admins (custom group)
   - managers (custom group)
   ...

users:
   - god (initial user)
   ...

Principals are mapped to global permission :term:`roles` or :term:`local roles`
(only for a specific context).


Roles (mapping to permissions):
...............................

Roles with example permission mapping:

    - reader: can view:
        view the proposal

    - contributor: can add content:
        add comment to the proposal
        add voting to the proposal

    - editor: can edit content:
        edit proposal

    - creator: edit meta stuff: permissions, transition to workflow states, ...:
        edit proposal
        change workflow state to draft
        change permissions

    - reviewer: do transition to specific workflow states:
        change workflow state to accepted/denied

    - manager: edit meta stuff: permissions, transition to workflow states, ...:
        add ...
        edit ...
        change workflow state ..
        change permissions

    - admin: create an configure the participation process, manage principals:
        set workflow
        manage principals

Roles are inherited within the object hierarchy in the database.
The creator is the principal who created the local context.
The creator role is automatically set for a specific local context and is not
inherited.

ACL (Access Control List):
...........................

List with ACEs (Access Control Entry): [<Action>, <Principal>, <Permission>]

Action: Allow | Deny
Principal: UserId | group:GroupID | role:RoleID
Permission: view, edit, add, ...

Every resource in the object hierarchy has a local ACL.

To check permission all ACEs are searched starting with the ACL of the
requested resource, and then searching the parent's ACLs recursively.
The Action of the first ACE with matching permission is returned.


Customizing
...........

1. map users to group
2. map roles to principals
3. use workflow system to add :term:`local roles` mapped to principals
4. manually add :term:`local roles` (change permission to allow others to edit)
5. map permissions to roles:
    - use only configuration for this
    - default mapping should just work for most use cases

Questions
---------

what is the difference between role and group, on a conceptual level?
(why do we need both?)  i'm assuming that groups are a pyramid
concept, and roles are something we want to build on top?

- For the basic pyramid authorization system there are only principals, no
  matter if you call them user/group or role.
  On our conceptual level we have a different semantic for user, group and role.
  You can see roles as groups with a default set of permissions.

is there multiple inheritance?

- no

can groups be members of groups?

- no. but it would be easy to implement that.

Do we need workflows at all?  or can we assume ACLs and roles don't change at
run time?

- For the year 2014: ACL won't change during runtime and workflows are not needed

Random notes (matthias):
------------------------
FIXME: cleanup the following stuff

draw a graph with all mappings, and mark them as
 - 1:n vs. n:1 vs. n:m
 - dynamic (workflows) vs. static (config files)

identify minimal subset that
 - satisfies requirements for merkator.
 - can be implemented efficiently, and the rest can be added efficiently later.

API
...

an operation is a tuple (user, resource, permission).  example::

    ( joe,
      /adhocracy/proposals/against_curtains/version_000043,
      edit )

we wants to
 - ask if an operation is allowed (so it can render an object as non-editable, for instance).
 - try an operation, and get a "denied" error that it can handle gracefully.

mappings from users, groups, roles to each other must be contained in
resources.  (and only visible to authorized users!)  (it is a security
requirement that these resources are in sync with the backend!)


notes from meeting with joka
............................

FIXME: If FE wants to ask BE about permissions, there are many ways to
implement this:

 - OPTIONS protocol (already implemented, and expressive enough to
   decide if we can eit a resource or not)

this is what we want to do for merkator.  future alternatives:

 - add permission object to meta api (CAVEAT: this makes version
   resources change unexpectedly).

 - change HTTP response to contain not only the resource but also
   permission information in a larger json object.

 - new http endpoint for permission requests.
