# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 08:48:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

SECRET_KEY = 'nosecret'

INSTALLED_APPS = [
    "tests.translation",
]

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
