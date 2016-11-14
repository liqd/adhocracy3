#!/bin/sh
grep -o -h "TR__[^\"']*" $(git ls-files | grep '\.\(html\|ts\)$') | sort | uniq | sed 's/\(TR__RESOURCE.*\)/\1\n\1_PLURAL/'
