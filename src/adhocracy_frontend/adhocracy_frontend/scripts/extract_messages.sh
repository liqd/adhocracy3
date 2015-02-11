#!/bin/sh

(
    git grep "{{[^{]*['\"]\s*|\s*translate" \
        | grep -o '{{[^{]*|\s*translate' \
        | sed "s/{{\s*[\"']//;s/[\"']\s*|\s*translate//";
    grep -o -h "TR__[^\"']*" $(git ls-files | grep '\.ts$');
) | sort | uniq
