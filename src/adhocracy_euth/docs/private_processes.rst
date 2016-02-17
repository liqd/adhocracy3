Private processes
=================

It is possible to define private processes in the EUth package.
Private processes cannot be viewed by registered users who do not
belong to the process.

In order to allow this, a few modifications have been done to the
default permissions in EUth:
- Authenticated (logged in) users do not become the 'participant'
role.
- anonymous and authenticated roles do not get the 'view' permission.


Administration
--------------
Following local roles must be created for every public processes::

     {"group:authenticated": {"role:participant"}}

Following local roles must be created for every private processes::

     {"name-of-process-participants": {"role:participant"}}

The users of the process must be assigned to the
"name-of-process-participants" group via the `import_users` script.
