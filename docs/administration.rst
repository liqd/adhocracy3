Administration
==============

Several console scripts are provided to facilitate the administration of
Adhocracy 3.

Workflow state
--------------

The state of the workflow can be changed with the `set_workflow_state`
command.

A relative path containing all the states to execute before reaching
the wanted state can be given. For example, assuming the current
workflow is the standard one and the process is located in
/organisation/workshop in the 'participate' state, we can type this
command to set it to 'closed' state::

    ./bin/set_workflow_state etc/development.ini /organisation/workshop evaluate result closed

An absolute path can be given instead of a relative one with the
`absolute` option. The following command will put the workflow in the
'closed' phase, whatever the current state is::

  ./bin/set_workflow_state --absolute etc/development.ini /organisation/workshop announce participate evaluate result closed

The current state and information about the workflow can be obtained with the `info` option::

    ./bin/set_workflow_state --info etc/development.ini /organisation/workshop


Resources
---------

Resources can be defined in JSON files and be imported with different
scripts.

.. caution:: The scripts are not using the validation provided by the
             REST API and can fail silently or create invalid data if
             provided with invalid inputs. A backup of the
             database should be done before executiong them.


Organisations and processes
+++++++++++++++++++++++++++

The `import_resources` script can be used to import organisations and processes::

    ./bin/import_resources etc/development.ini src/adhocracy_core/adhocracy_core/scripts/resources_sample.json

Groups and users
++++++++++++++++

Use the `import_groups` script to import groups::

    ./bin/import_groups etc/development.ini src/adhocracy_core/adhocracy_core/scripts/groups_sample.json

and  `import_users` script to import initial users::

    ./bin/import_users etc/development.ini src/adhocracy_core/adhocracy_core/scripts/users_sample.json

The JSON file describing the users is used to assign users to groups, so groups need to be imported before users.

:term:`Local roles <Local role>` can also be defined::

    ./bin/import_local_roles  etc/development.ini src/adhocracy_core/adhocracy_core/scripts/local_roles_sample.json

Since the local roles JSON file references resources, users and
groups, it is necessary to import them before executing the script.

Badges
++++++

Badges can be imported with the `import_resources` script::

    ./bin/import_resources etc/development.ini src/adhocracy_core/adhocracy_core/resources/user_badges_sample.json

Badges can be assigned to resources with the `assign_badges` script::

    ./bin/assign_badges etc/development.ini ./src/adhocracy_core/adhocracy_core/scripts/user_badge_assignments_sample.json


