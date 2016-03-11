#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.utils.functional import empty
from django.test.utils import get_runner


if __name__ == "__main__":

    def run_tests(subtest):

        test_module = 'tests.' + subtest
        os.environ['DJANGO_SETTINGS_MODULE'] = test_module + '.settings'
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        failures = test_runner.run_tests([test_module])
        return bool(failures)

    ret = run_tests(sys.argv[1])
    sys.exit(ret)

