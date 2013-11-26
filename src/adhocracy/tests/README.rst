


This document contains project-specific documentation of the testing
tool chain and setup.



code coverage tools for css
~~~~~~~~~~~~~~~~~~~~~~~~~~~

[matthias suggests helium-css.]


helium-css
  - github, javascript, seems to be most suitable for hacking

dust me / roundup
  - firefox plugin

pagespeed
  - google project for page tuning; does a bit more than css code coverage.



code coverage tools for js
~~~~~~~~~~~~~~~~~~~~~~~~~~

[matthias suggests JSCover.]


https://github.com/tntim96/JSCover
  - runs in every browser.  allows dom interaction.  supports many test tools.
  - java.
  - jenkins plugin.
  - runs its own web server, or a proxy.

http://siliconforks.com/jscoverage/
  - predecessor of JSCover (obsolete)

http://timurstrekalov.github.io/saga/
  - similar approach so JSCover.
  - java.
  - better headless support?

http://github.com/qfox/Heatfiler
  - purely js.
  - compiles 'ping' statements into js code (at run time?) that records number of executions per expression.
  - http://heatfiler.qfox.nl  (demo)
  - http://qfox.nl/weblog/268  (blog)
  - not very active.

https://github.com/coveraje/coveraje
  - similar to headfiler.
  - seems more active.
  - not very mature.  "one file only".
  - seems to work better on node than in browsers.

jsChilicat
  - large test framework supporting coverage reports.
  - reports look ok.
  - we already have testing tools.

https://code.google.com/p/js-test-driver/wiki/CodeCoverage
  - java

https://code.google.com/p/script-cover/
  - chrome plugin or javascript code (not clear).
  - very poorly documented.
