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

frontend unit tests:

    A.  Integrated with py.test::

            bin/py.test ./src/adhocracy/adhocracy/frontend/tests/unit/

    B.  In browser::

            make -C ./src/adhocracy/adhocracy/frontend/static/js/ compile_tests_browser
            xdg-open http://localhost:6541/frontend_static/test.html

        Make sure backend is running (or some means of delivering html
        and js to the browser).

        This is the best way to develop, as it lets you run tests
        indiviually and repeatedly and enter the debugger.

        .. note::

           In the debugger, it helps to disable the script tag about
           blanket in test.html.  You can do this thusly::

               make -C ./src/adhocracy/adhocracy/frontend/static/js/ compile_tests_browser test_no_blanket
               xdg-open http://localhost:6541/frontend_static/test-no-blanket.html

    C.  With node.js::

            make -C ./src/adhocracy/adhocracy/frontend/static/js/ compile_tests_node
            bin/jasmine-node ./src/adhocracy/adhocracy/frontend/static/js/

        .. note::

           Node only works with the commonjs module system;
           whereas the frontend currently uses requirejs and the amd
           module system (rationale: requirejs is more powerful with
           importing module-system-oblivious libraries like angular,
           underscore, ...).  You know that you have run into this
           problem if this appears in your browser console::

               Uncaught Error: Module name "Adhocracy/UtilSpec" has not been loaded yet for context: _. Use require([])
               http://requirejs.org/docs/errors.html#notloaded

           In order for the javascript code to work in the browser, you
           need to revert to adm::

               make -C ./src/adhocracy/adhocracy/frontend/static/js/ compile_tests_browser

frontend functional tests::

    bin/py.test ./src/adhocracy/adhocracy/frontend/tests/functional

frontend acceptance tests::

    bin/py.test tests/

   .. note::
      The embed tests assume aliases for localhost to exist. If it is
      not already there, please add the following line to /etc/hosts::

          127.0.0.1  adhocracy.embeddee.goo adhocracy.embedder.gaa

      then start the testrunner with enabled embed testing::

          bin/py.test --run_embed_tests tests

run backend functional tests::

    bin/py.test -m"functional" src/adhocrac/adhocracy/websocket src/adhocracy_sample/adhocracy_sample/docs

run backend unit tests and show python test code coverage::

    bin/py.test_run_unittests_with_coverage

run all tests::

    bin/py.test_run_all

delete database (works best on development systems without valuable data!)::

    rm -f ./var/Data.*
    supervisorctl restart all

Generate html documentation
---------------------------

Recreate api documentation source files::

    bin/sphinx-apidoc -fo docs/source src/adhocracy  **/test* 

Generate html documentation::

    bin/sphinx_build_adhocracy

