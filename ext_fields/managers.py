# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:08:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from django.db import models
from .exceptions import ExFieldExceptionCannotSet
from .exceptions import ExFieldExceptionCannotDel
from .exceptions import ExFieldUnableSaveFieldType


class InternalExFieldsManager:

    def __init__(self, owner, fields_tables, fields_models):
        self._owner = owner
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    def _get_new_queryset(self):
        return self._owner.objects

    def _get_filtering(self, argv):
        qoptions = (
            'exact',
            'iexact',
            'contains',
            'icontains',
            'in',
            'gt',
            'gte',
            'lt',
            'lte',
            'startswith',
            'istartswith',
            'endswith',
            'iendswith',
            'range',
            'year',
            'month',
            'day',
            'week_day',
            'hour',
            'minute',
            'second',
            'isnull',
            'search',
            'regex',
            'iregex',
            'have',
        )

        p = None
        for fname, fopt in argv.items():
            q = None

            opt = 'exact'
            opts_path = fname.split('__')[-1]
            if opts_path in qoptions:
                opt = opts_path
                fname = fname[:len(fname)-len(opt)-2]

            if opt == 'have':
                for tname, ttype in self._fields_tables.items():
                    x = models.Q(((tname+'__field').lower(), fname,))
                    if fopt:
                        q = (q | x) if q else x
                    else:
                        q = (q & (~x)) if q else ~x
            else:
                for tname, ttype in self._fields_tables.items():
                    if type(fopt) is ttype[0]:
                        q = models.Q(((tname+'__value').lower()+'__'+opt, fopt,)) \
                            & models.Q(((tname+'__field').lower(), fname,))
                        break
                else:
                    raise ExFieldUnableSaveFieldType('Cannot select based on given type!')

            if not p:
                p = q
            else:
                p = p & q

        return p

    def filter(self, queryset=None, **argv):
        if not queryset:
            queryset = self._get_new_queryset()
        return queryset.filter(self._get_filtering(argv)).distinct()

    def exclude(self, queryset=None, **argv):
        if not queryset:
            queryset = self._get_new_queryset()
        return queryset.exclude(self._get_filtering(argv)).distinct()

    def distinct_fields(self, queryset=None):
        ret = list()

        if not queryset:
            queryset = self._get_new_queryset()

        columns = map(lambda x: (x+'__field').lower(), self._fields_tables.keys())
        fields = queryset.values(*columns).distinct()

        for entry in fields:
            for value in entry.values():
                if value is not None and value not in ret:
                    ret.append(value)

        return ret


class ExFieldsManager(object):

    def __init__(self, fields_tables, fields_models):
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    def __get__(self, instance, owner):
        return InternalExFieldsManager(owner, self._fields_tables,
            self.__ex_fields_class)

    def __set__(self, instance, value):
        raise ExFieldExceptionCannotSet('Cannot set ext_fields_manager property')

    def __del__(self, instance):
        raise ExFieldExceptionCannotDel('Cannot del ext_fields_manager property')

