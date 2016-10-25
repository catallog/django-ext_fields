# -*- coding: utf-8 -*-
# @Date    : 2016-01-26 18:26
# @Author  : Basask (basask@gmail.com)

from __future__ import unicode_literals
from django.conf import settings
from django.utils.dateparse import parse_datetime
from ext_fields.constants import VALUE_PREFIX, TYPEMAP


DETECT_DATE = getattr(settings, "EXTFIELDS_DETECT_DATE", False)


class Mapper(object):

    def __init__(self, model_class, *args, **kwargs):
        self.translated = kwargs.get('translate', True)
        self.model_class = model_class

    def get_field_related(self, *args):
        chunks = [self.model_class._meta.model_name]
        chunks += args
        return ('__'.join(chunks)).lower()

    @staticmethod
    def get_value_map(value):
        value_type = type(value)
        if DETECT_DATE and value_type in [str, unicode]:
            if parse_datetime(value):
                return 'date'
        for k, v in TYPEMAP.items():
            if value_type in v:
                return k
        return None

    @classmethod
    def get_value_field_name(cls, value):
        return VALUE_PREFIX + cls.get_value_map(value)

    @staticmethod
    def get_row_value(row):
        def last_nonempty_field(a, b):
            val = getattr(row, VALUE_PREFIX + b)
            if val is not None:
                return val
            return a
        return reduce(last_nonempty_field, TYPEMAP.keys(), None)

    @classmethod
    def get_dict_val(cls, value):
        vm = cls.get_value_map(value)
        keys = TYPEMAP.keys()
        return {VALUE_PREFIX + k: value if vm == k else None for k in keys}
