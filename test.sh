#!/bin/bash

coverage run --source='ext_fields' runtests.py
coverage annotate -d coverage_annotate
coverage report
