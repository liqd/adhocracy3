Permission system
-----------------

Principals (global/local mapping to Roles)
..........................................

- groups
   - Authenticated (all authenticated users, pyramid internal name)
   - Everyone (all authenticated and anonymous users, pyramid internal name)
   - managers (custom group)
   - admins (custom group)
   - gods (custom group, no permssion checks)
   ...

- users
   - god
   ...

Groups can not be members of groups.


Roles (global mapping to permissions)
.....................................

  local (inheritance):

    - reader: can read:
        read the proposal

    - contributor: can add content:
        add comment to the proposal

    - editor: can edit content:
        edit proposal

    - manager: edit meta stuff: permissions, workflow state, ...:
        accept/deny proposal

    - admin: create an configure the participation process
             manage principals

  local (no inheritance):

    - creator: principal who created the local context:
        ....


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

(There is no multiple inheritance, so this algorithm is sound.)


Customizing
...........

1. map users to group
2. map roles to group/(user)
3. use workflow system to locally change:
        - mapping role to principals
        - mapping permission to role
4. locally change mapping role to principals
5. map permissions to roles:
        - use only configuration for this
        - default mapping should just work for most use cases)


API
---

The user object must contain a list of roles and a list of groups she
is a member of.  This is necessary because the UI looks different for
different roles (at the very least, we want to see a different icon
for every role in the login widget).

If the FE sends a request to the BE that it has no authorisation for,
it will receive an error (depending on the situation either 4xx to
conceal the existence of secret resources, or 3xx to explicitly deny
access).

There are (at least) four approaches to implement an API that the FE
can use to query BE about permissions without actually performin an
access operation an observing the response:

1. OPTIONS protocol.  This is expressive enough to decide if user is
   allowed to edit a resource or not, but not enough to inspect or
   edit permissions of self (by ordinary users) or other users (by
   admin).

2. (future work) Add permission object to meta api (CAVEAT: this makes
   version resources change unexpectedly).

3. (future work) Change HTTP response to contain not only the resource
   but also permission information in a larger json object.

4. (future work) New HTTP end-point for permission requests.


FIXME: Open questions
---------------------

first two sections are confusing.  they do not explain what users,
groups, roles are, what distinguishes them, and their mechanics.

define global, local?

does "inheritance" always mean "content type inheritance"?

what is the difference between role and group, on a conceptual level?
why do we want both?  what can i do with a role but not with a group,
and vice versa?
