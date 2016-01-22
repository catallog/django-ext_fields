#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    tests_repo='tests.%s'%sys.argv[1]
    os.environ['DJANGO_SETTINGS_MODULE'] = tests_repo + '.settings'
    print os.environ['DJANGO_SETTINGS_MODULE']
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([tests_repo])
    sys.exit(bool(failures))
