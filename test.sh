#!/bin/bash

function run_test {
    coverage run -p --source='ext_fields' runtests.py $1
    # coverage annotate -d "coverage_annotate_$1"
}

if [ $# -gt 0 ]; then
    if [ -d tests/$1 ]; then
        run_test $1
    else
        echo "There's no module '$1' in tests!"
        exit 1
    fi
else
    for i in tests/* ; do
        if [ -d "$i" ]; then
            run_test `basename $i`
        fi
    done
fi

coverage combine
coverage annotate -d "coverage_annotate"
coverage report
codecov

