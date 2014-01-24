*******************************
Recipe for installing ruby gems
*******************************

Using this recipe you can easily install ruby gems packages into buildout
environment.

All executable files from gem packages are available in ``bin-directory``.

Usage
=====

::

    [buildout]
    parts =
        rubygems

    [rubygems]
    recipe = rubygemsrecipe
    gems =
        sass
        compass==0.10

After running buildout you can use SASS from buildout environment::

    ./bin/sass --version

Options
=======

gems
    list of gem package names, also you can specify gem version, example:
    ``sass==3.1.1``.

version
    rubygems version, if not specified, recipe will try to find most recent
    version.

ruby-executable
    A path to a Ruby executable. Gems will be installed using this executable.
