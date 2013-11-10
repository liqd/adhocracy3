

a3 testing methods and tools
----------------------------


overview of options
~~~~~~~~~~~~~~~~~~~

http://visionmedia.github.io/mocha/
 - recommended by tobias

https://github.com/douglascrockford/JSCheck/blob/master/jscheck.js
 - quickcheck for js by douglas crockford ("javascript - the good parts")
 - no 'shrink' (i think)
 - otherwise pretty complete, with 750 loc and trivial build process ('cp')

https://bitbucket.org/darrint/qc.js/
 - quickcheck
 - a bit rough and unsupported (?)

https://github.com/VoQn/Macchiato
 - quickcheck
 - interesting, but not very active

http://qunitjs.com/
 - unit-test
 - small, simple, active
 - well-written, simple docs (cookbook)
 - not that many features

https://github.com/puffnfresh/bilby.js
 - actually a lib for functional-style js development that supports quickcheck

http://busterjs.org/
 - used by obviel
 - mature

http://seleniumhq.org/
 - firefox plugin for recording tests.  looks neat!

https://github.com/pivotal/jasmine
 - has that annoying *spec/expect pseudo-slang syntax

http://code.google.com/p/js-test-driver
 - looks a little stalled.

http://stackoverflow.com/questions/300855/javascript-unit-test-tools-for-tdd
 - collection of (often dead) projects.


decision process (proposal
~~~~~~~~~~~~~~~~~~~~~~~~~~

 - write tests for existing prototype in jscheck.

 - try out jscheck-driven development on new feature.

 - check selenium, qc, qunit for features that we want and that jscheck does not have.

 - sketch build-bot with buster.
