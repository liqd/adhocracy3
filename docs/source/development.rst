Development
============

Development
-----------

Use test driven development and check code style bevore pushing commits
(see `Coding Style Guideline` ).

Manually check pyflake, pep257::

    bin/check_code src/adhocracy src/adhocracy_sample

Example Vim config according to coding guideline::

    https://github.com/liqd/vim_config


Install Robotframework
----------------------

install robotframework for acceptance testing ::

    cd robotframework/
    python2.7 bootstrap.py
    bin/buildout


Running the Testsuite
---------------------

backend ::

    bin/py.test src/adhocracy src/adhocracy_sample

frontend tests::

    bin/py.test ./src/adhocracy/adhocracy/frontend/tests/

acceptance tests::

    bin/py.test tests_acceptance
