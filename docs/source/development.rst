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


Running the Testsuite
---------------------

backend unit, integration and acceptance tests::

    bin/py.test src/adhocracy src/adhocracy_sample

frontend unit tests:

    A.  Integrated with py.test::

            bin/py.test ./src/adhocracy/adhocracy/frontend/tests/unit/

    B.  In browser::

        xdg-open http://localhost:6541/frontend_static/test.html

    C.  With node.js::

        bin/tsc -m commonjs ./src/adhocracy/adhocracy/frontend/static/js/Adhocracy*.ts
        bin/jasmine-node ./src/adhocracy/adhocracy/frontend/static/js/

frontend functional tests::

    bin/py.test ./src/adhocracy/adhocracy/frontend/tests/functional

frontend acceptance tests::

    bin/py.test tests_acceptance

run all tests::

    bin/py.test_run_all
