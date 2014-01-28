Change History
**************

0.1.7 (2012-05-24)
==================

- Feature: added 'ruby-executable' option, thanks to desaintmartin.

0.1.6 (2012-04-26)
==================

- Fix: pass all arguments as separate arguments instead of a single string.

0.1.5 (2012-01-06)
==================

- Fix: use each version only for the line it's specified in.

0.1.4 (2012-01-03)
==================

- You can specify a version for each gem with a syntax similar to python eggs.


0.1.3 (2011-12-28)
==================

- Added 'version' option to specify explicit rubygems version.

0.1.2 (2011-11-09)
==================

- New version of rubygems includes symlinks in .tgz archyve and extracted by
  setuptools.archive_util extractor ignores all symlinks. This causes missing
  files in extracted folder. Now rubygemsrecipe downloads .zip archyve instead
  of .tgz.

0.1.1 (2011-10-04)
==================

- Fixed issue with name of gem executable, which can be different depending on
  how ruby is istalled on host system.

- Install rubygems if gem executable is not found, not rubygems direcotry.

0.1 (2011-09-07)
================

- Initial public release.
