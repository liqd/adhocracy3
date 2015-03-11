# extract package dependencies and output them in dot language.
# see `man dot` for options to display the output.
# example usage: ./deps2dot.sh | dot -T png -o deps.png && xdg-open deps.png

echo 'digraph adhocracy_frontend {'

git grep -l 'moduleName = ' | grep '\.ts$' | while read path; do
    package=`grep 'moduleName = ' $path | sed 's/.*moduleName = "adh\(.*\)";$/\1/'`
    echo "  $package;"
    grep '\.moduleName' $path | sed 's/ *\(.*\)\.moduleName,\?$/\1/' | sed 's/^Adh//' | while read import; do
        echo "  $import->$package;"
    done
done

echo '}'
