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

with server setup and teardown (wsgi) ::

    bin/py.test src/adhocracy src/adhocracy_sample
