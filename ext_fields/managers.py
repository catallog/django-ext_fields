# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:08:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from ext_fields.exceptions import ExFieldExceptionCannotSet
from ext_fields.exceptions import ExFieldExceptionCannotDel
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from ext_fields.typemapper import TypeMapper


class InternalExFieldsManager(TypeMapper):

    def __init__(self, model_class, owner):
        self.__ex_fields_class = model_class
        self.__owner = owner
        TypeMapper.__init__(self, model_class)

    def _get_new_queryset(self):
        return self.__owner.objects

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

        query = None
        for fname, fopt in argv.items():
            opt = 'exact'
            opts_path = fname.split('__')[-1]
            if opts_path in qoptions:
                opt = opts_path
                fname = fname[:len(fname)-len(opt)-2]

            sub_query = Q( ( self.get_field_related('field'), fname,) )
            if opt == 'have':
                query = sub_query if fopt else ~sub_query
            else:
                if not self.get_value_map(fopt):
                    raise ExFieldUnableSaveFieldType('Value assigned to query not supported in ' + fname)
                value_field = self.get_value_field_name(fopt)
                lookup_value = self.get_field_related(value_field, opt)
                query = Q( ( self.get_field_related('field'), fname,) ) & Q( (lookup_value, fopt,) )
        return query

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
        fields = queryset.values(self.get_field_related('field')).distinct()

        for entry in fields:
            for value in entry.values():
                if value is not None and value not in ret:
                    ret.append(value)
        return ret


class ExFieldsManager(object):

    def __init__(self, model_class):
        self.__ex_fields_class = model_class

    def __get__(self, instance, owner):
        return InternalExFieldsManager(self.__ex_fields_class, owner)

    def __set__(self, instance, value):
        raise ExFieldExceptionCannotSet('Cannot set ext_fields_manager property')

    def __del__(self, instance): #pragma:no cover
        raise ExFieldExceptionCannotDel('Cannot del ext_fields_manager property')

