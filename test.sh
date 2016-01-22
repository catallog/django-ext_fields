#!/bin/bash

ALL='flat translated'

function runtest {
    coverage run --source='ext_fields' runtests.py $1
    coverage annotate -d coverage_annotate/$1
    coverage report
}

if [ $# -gt 0 ]; then
    runtest $1
else
    for i in $ALL;
    do
        $0 $i
    done
fi
