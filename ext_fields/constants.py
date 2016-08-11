# -*- coding: utf-8 -*-
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals
from datetime import datetime


VALUE_PREFIX = 'value_'

TYPEMAP = {
    'int': [int],
    'float': [float],
    'date': [datetime],
    'str': [str, unicode]
}
