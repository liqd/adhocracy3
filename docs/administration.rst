Administration
==============

Several console scripts are provided to facilitate the administration of
Adhocracy 3.

Workflow state
--------------

The state of the workflow can be changed with the `set_workflow_state`
command. The `-h` flag can be used to see a full description of the
options.

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

The `ad_import_resources` script can be used to import organisations and processes::

    ./bin/ad_import_resources etc/development.ini src/adhocracy_core/adhocracy_core/scripts/resources_sample.json

Groups and users
++++++++++++++++

Use the `ad_import_groups` script to import groups::

    ./bin/ad_import_groups etc/development.ini src/adhocracy_core/adhocracy_core/scripts/groups_sample.json

and  `ad_import_users` script to import initial users::

    ./bin/ad_import_users etc/development.ini src/adhocracy_core/adhocracy_core/scripts/users_sample.json

The JSON file describing the users is used to assign users to groups, so groups need to be imported before users.

:term:`Local roles <Local role>` can also be defined::

    ./bin/ad_import_local_roles  etc/development.ini src/adhocracy_core/adhocracy_core/scripts/local_roles_sample.json

Since the local roles JSON file references resources, users and
groups, it is necessary to import them before executing the script.

Badges
++++++

Badges can be imported with the `ad_import_resources` script::

    ./bin/ad_import_resources etc/development.ini src/adhocracy_core/adhocracy_core/resources/user_badges_sample.json

Badges can be assigned to resources with the `ad_assign_badges` script::

    ./bin/ad_assign_badges etc/development.ini ./src/adhocracy_core/adhocracy_core/scripts/user_badge_assignments_sample.json


