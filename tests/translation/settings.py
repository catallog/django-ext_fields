# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 08:48:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/



import os


SECRET_KEY = 'nosecret'

INSTALLED_APPS = [
    "tests.translation",
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

LANGUAGE_CODE = 'en-us'
EXTFIELDS_TRANSLATE = True
EXTFIELDS_FALLBACK_TRANSLATE = True

# datetime settings
USE_TZ = True
EXTFIELDS_DETECT_DATE = True
