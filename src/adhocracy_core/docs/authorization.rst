Permission system
-----------------

Principals
..........

There are two types of principals users and groups (:term:`principal`).
On the technical level, roles are also called principles.

groups (set of users):

   - authenticated (all authenticated users)
   - system.Everyone (all authenticated and anonymous users, standard group)
   - gods (initial custom group, no permission checks)
   - admins (custom group)
   - managers (custom group)
   - ...

users:
   - god (initial user)
   - ...

Principals are mapped to a set of global permissions(:term:`role`)
and local permissions for a specific context (:term:`local role`)


Roles (mapping to permissions)
..............................

Roles with example permission mapping:

    - reader: can view:
        view the proposal

    - annotator: can add content metadata/annotations
        add comment to the proposal
        add voting to the proposal
        add rating to the proposal
        add tag to the proposal

    - contributor: can add content:
        add proposal

    - editor: can edit content:
        edit proposal

    - creator: edit meta stuff: permissions, transition to workflow states, ...:
        edit proposal
        change workflow state to draft
        change permissions

    - reviewer: do transition to specific workflow states:
        change workflow state to accepted/denied

    - manager: delete, edit meta stuff: permissions, transition to workflow states, ...:
        'delete' illegal content
        change workflow state ..
        change permissions

    - admin: create an configure the participation process, manage principals:
        add participation process
        set workflow
        manage principals

Mappings of principals to local roles are associate with resources and
are inherited within the object hierarchy in the database.
The creator is the principal who created the local context.
The creator role is automatically set for a specific local context and is not
inherited.


ACL (Access Control List)
.........................

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
3. use workflow system to locally add roles to principals.
4. locally add :term:`local role`s (change permission to allow others to edit)
5. map permissions to roles:

    - use only configuration for this
    - default mapping should just work for most use cases


Questions
---------

What is the difference (conceptually) between a role and a group?

- For the basic pyramid authorization system there are only principals, no
  matter if you call them user/group or role.
  On our conceptual level we have a different semantic for user, group and role.
  You can see roles as groups with a default set of permissions.

is there multiple inheritance?

- no

does "inheritance" always mean "content type inheritance"?

- in this context `inheritance` means inheritance from parent to child in
  the object hierarchy

can groups be members of groups?

- no. but it would be easy to implement that.

Do we need workflows at all?  or can we assume ACLs and roles don't change at
run time?

- For the year 2014: ACL won't change during runtime and workflows are not needed


API
---

The user object must contain a list of roles and a list of groups she
is a member of.  This is necessary because the UI looks different for
different roles (at the very least, we want to see a different icon
for every role in the login widget).

If the FE sends a request to the BE that it has no authorization for,
it will receive an error (depending on the situation either 4xx to
conceal the existence of secret resources, or 3xx to explicitly deny
access).

There are (at least) four approaches to implement an API that the FE
can use to query BE about permissions without actually performing an
access operation an observing the response:

1. OPTIONS protocol.  This is expressive enough to decide if user is
   allowed to edit a resource or not, but not enough to inspect or
   edit permissions of self (by ordinary users) or other users (by
   admin).

2. (future work) Add permission object to meta API (CAVEAT: this makes
   version resources change unexpectedly).

3. (future work) Change HTTP response to contain not only the resource
   but also permission information in a larger JSON object.

4. (future work) New HTTP end-point for permission requests.
