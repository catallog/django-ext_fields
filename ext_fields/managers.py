# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:08:52
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from django.db.models import Q
from ext_fields.exceptions import ExFieldExceptionCannotSet
from ext_fields.exceptions import ExFieldExceptionCannotDel
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from ext_fields.mapper import Mapper


class InternalExFieldsManager(Mapper):

    def __init__(self, model_class, owner):
        self.__owner = owner
        Mapper.__init__(self, model_class)

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
            'unaccent'
        )

        query = None
        for fname, fopt in argv.items():
            opt = 'exact'
            opts_path = fname.split('__')[1:]
            valid_fnames = []
            for opp in opts_path:
                if opp in qoptions:
                    opt = opp
                    valid_fnames.append(opp)
                    # fname = fname[:len(fname) - len(opt) - 2]
            # fname = '__'.join(valid_fnames)
            fname = fname.split('__')[0]
            if len(valid_fnames):
                opt = '__'.join(valid_fnames)

            sub_query = Q((self.get_field_related('field'), fname,))
            if opt == 'have':
                query = sub_query if fopt else ~sub_query
            else:
                if not self.get_value_map(fopt):
                    raise ExFieldUnableSaveFieldType('Value assigned to query not supported in ' + fname)
                value_field = self.get_value_field_name(fopt)
                lookup_value = self.get_field_related(value_field, opt)
                query = Q((self.get_field_related('field'), fname,)) & Q((lookup_value, fopt,))
        return query

    def filter(self, queryset=None, **argv):
        queryset = queryset or self._get_new_queryset()
        return queryset.filter(self._get_filtering(argv)).distinct()

    def exclude(self, queryset=None, **argv):
        queryset = queryset or self._get_new_queryset()
        return queryset.exclude(self._get_filtering(argv)).distinct()

    def distinct_fields(self, queryset=None):
        queryset = queryset or self._get_new_queryset()
        fields = queryset.values(self.get_field_related('field')).distinct()
        return map(lambda a: a.values()[0], fields)


class ExFieldsManager(object):

    def __init__(self, model_class):
        self.__ex_fields_class = model_class

    def __get__(self, instance, owner):
        return InternalExFieldsManager(self.__ex_fields_class, owner)

    def __set__(self, instance, value):
        raise ExFieldExceptionCannotSet('Cannot set ext_fields_manager property')

    def __del__(self, instance):  # pragma:no cover
        raise ExFieldExceptionCannotDel('Cannot del ext_fields_manager property')
