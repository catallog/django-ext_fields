# -*- coding: utf-8 -*-
# @Date    : 2016-01-26 18:26
# @Author  : Basask (basask@gmail.com)

from __future__ import unicode_literals
from datetime import datetime


class Mapper(object):

    _PREFIX = 'value_'

    TYPEMAP = {
        'int': [ int ],
        'str': [ str, unicode ],
        'float': [ float ],
        'date': [ datetime ]
    }

    def __init__(self, model_class):
        self.model_class = model_class

    def get_field_related(self, *args):
        chunks = [ self.model_class._meta.model_name ]
        chunks += args
        return ( '__'.join(chunks)).lower()

    def get_value_map(self, value):
        first_valid_match = lambda a,b: b[0] if type(value) in b[1] else a
        return reduce(first_valid_match, self.TYPEMAP.items(), None)

    def get_value_field_name(self, value):
        return self._PREFIX + self.get_value_map(value)

    def get_row_value(self, row):
        last_nonempty_field = lambda a, b: a or getattr(row, self._PREFIX + b)
        return reduce(last_nonempty_field, self.TYPEMAP.keys(), None)

    def get_dict_val(self, value):
        vm = self.get_value_map(value)
        return  { self._PREFIX + k : value if vm == k else None for k in self.TYPEMAP.keys() }
