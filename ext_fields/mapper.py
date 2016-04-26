# -*- coding: utf-8 -*-
# @Date    : 2016-01-26 18:26
# @Author  : Basask (basask@gmail.com)

from __future__ import unicode_literals
from datetime import datetime
from django.conf import settings
from django.utils.dateparse import parse_datetime

DETECT_DATE = getattr(settings, "EXTFIELDS_DETECT_DATE", False)


class Mapper(object):

    _PREFIX = 'value_'

    TYPEMAP = {
        'int': [int],
        'float': [float],
        'date': [datetime],
        'str': [str, unicode]
    }

    def __init__(self, model_class, *args, **kwargs):
        self.translated = kwargs.get('translate', True)
        self.model_class = model_class

    def get_field_related(self, *args):
        chunks = [self.model_class._meta.model_name]
        chunks += args
        return ('__'.join(chunks)).lower()

    def get_value_map(self, value):
        value_type = type(value)
        if DETECT_DATE and value_type in [str, unicode]:
            if parse_datetime(value):
                return 'date'
        for k, v in self.TYPEMAP.items():
            if value_type in v:
                return k
        return None

    def get_value_field_name(self, value):
        return self._PREFIX + self.get_value_map(value)

    def get_row_value(self, row):
        def last_nonempty_field(a, b):
            val = getattr(row, self._PREFIX + b)
            if val is not None:
                return val
            return a
        return reduce(last_nonempty_field, self.TYPEMAP.keys(), None)

    def get_dict_val(self, value):
        vm = self.get_value_map(value)
        return {self._PREFIX + k: value if vm == k else None for k in self.TYPEMAP.keys()}
