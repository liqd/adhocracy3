#!/bin/sh

if [ -z ${1+x} ]; then
    projects="adhocracy_frontend mercator meinberlin spd s1"
else
    projects=$1;
fi

for project in $projects; do
    echo "-- Building \"$project\""

    builddir="styleguides/$project"

    mkdir -p $builddir
    find $builddir -type l -exec rm {} +
    ln -s "$(pwd)/src/current/current/build/lib" "$builddir/."

    # merge static directories
    for dir in `printf "src/$project/$project/static\nsrc/adhocracy_frontend/adhocracy_frontend/static" | uniq`; do
        cp -ans `readlink -f $dir`/. $builddir
    done

    # create sass config
    cat <<EOF > Gruntfile_${project}.js
module.exports = function(grunt) {
    grunt.initConfig({
        sass: {
            options: {
                sourceMap: true,
                outputStyle: "compressed"
            },
            dist: {
                files: {
                    "$builddir/stylesheets/a3.css": "$builddir/stylesheets/scss/a3.scss",
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-sass');
};
EOF

    # create hologram config
    cat <<EOF > etc/hologram_${project}.yml
source: `realpath $builddir`/stylesheets/scss
destination: `realpath $builddir`/styleguide
documentation_assets: ../docs/styleguide_assets
index: base
EOF

    # run hologram
    bin/grunt --gruntfile "Gruntfile_${project}.js" sass
    bin/hologram etc/hologram_${project}.yml

    # clean up
    find $builddir -type l | grep '\(images\|fonts\)' | while read file; do
        cp --remove-destination "$(readlink $file)" $file
    done
    sed -i 's/\/static/../g' $builddir/styleguide/*.html $builddir/stylesheets/a3.css
    find $builddir -type l -exec rm {} +
    find $builddir -type d -empty -delete

    echo
done

{
    echo "<html>"
    echo "<body>"
    echo "<h1>Styleguides</h1>"
    echo "<ul>"
    for project in $projects; do
        echo "    <li><a href=\"$project/styleguide/\">$project</a></li>"
    done
    echo "</ul>"
    echo "</body>"
    echo "</html>"
} > styleguides/index.html