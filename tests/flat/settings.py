# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 08:48:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

import os


SECRET_KEY = 'nosecret'

INSTALLED_APPS = [
    "tests.flat",
]


if 'TRAVIS' in os.environ:
    database = os.environ.get('TEST_DATABASE')
    print "Testing in:", database
    if database == 'postgres':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'travisci',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'localhost',
                'PORT': '',
            }
        }
    if database == 'sqlite3':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'database.db',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '',
            }
        }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'database.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

EXTFIELDS_TRANSLATE = False
EXTFIELDS_FALLBACK_TRANSLATE = False

EXTFIELDS_DETECT_DATE = False
