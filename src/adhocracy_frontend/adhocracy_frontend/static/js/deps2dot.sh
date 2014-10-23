# extract package dependencies and output them in dot language.
# see `man dot` for options to display the output.
# example usage: ./deps2dot.sh | dot -T png -o deps.png && xdg-open deps.png

echo 'digraph adhocracy_frontend {'

git grep -l 'moduleName = ' | while read path; do
    package=`echo $path | sed 's/.*Packages\/\([^/]*\)\/.*$/\1/'`
    grep '\.moduleName' $path | sed 's/ *\(.*\)\.moduleName,\?$/\1/' | sed 's/^Adh//' | while read import; do
        echo "  $import->$package;"
    done
done

echo '}'
