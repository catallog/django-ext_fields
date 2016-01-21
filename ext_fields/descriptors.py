# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:51:16
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from django.utils import translation
from django.conf import settings
from django.db.models import Q


class ExFieldsDescriptors(object):
    def __init__(self, fields_tables, fields_models):
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    def _get_new_queryset(self, owner, instance):
        return owner.objects.filter(pk=instance.pk)


    def _build_filters(self, field, value):
        return reduce(
                lambda a,b: a | b ,
                map(lambda x: Q(**{ (x+'__'+field).lower():value}),self._fields_tables.keys())
            )

    def __get__(self, instance, owner):
        if '__extendedFieldsCache' not in instance.__dict__:
            instance.__extendedFieldsCache = dict()

            lang = translation.get_language()
            queryset = self._get_new_queryset(owner, instance)

            columns_fields = map(lambda x: (x+'__field').lower(), self._fields_tables.keys())
            columns_values = map(lambda x: (x+'__value').lower(), self._fields_tables.keys())
            columns = columns_fields + columns_values

            filters = self._build_filters('lang', lang)
            fields = queryset.filter(filters).values(*columns).distinct()

            for row in fields:
                vl = {}
                for k, v in row.items():
                    if v != None:
                        ftname = k[:-5]
                        ttname = k[-5:]

                        vl[ftname] = vl[ftname] if ftname in vl else {}
                        vl[ftname][ttname] = v

                for k, v in vl.items():
                    instance.__extendedFieldsCache[v['field']] = v['value']

        return instance.__extendedFieldsCache

    def __set__(self, instance, value):
        self.__delete__(instance)
        if (type(value) is tuple):
            if len(value) is not 2:
                raise ExFieldInvalidTypeSet('on setting ext_fields: Invalid lenght'
                    +' for tuple, len(value) must be 2, first item with key, second'
                    +' the holder value')
            if type(value[0]) not in (str, unicode,):
                raise ExFieldInvalidTypeSet('on setting ext_fields, first field on '
                    +'property tuple must be str with field name')

            if value[1] is None:
                return self._delete_field(instance, value[0])

            for tname, ttype in self._fields_tables.items():
                if ttype[0] is type(value[1]):
                    self._set_field(tname, instance, value[0], value[1])
                    break
            else:
                raise ExFieldUnableSaveFieldType('for now only str, int, float and datetime'
                    +'can be used as extended fields')

        elif type(value) is list:
            [ self.__set__(instance, v) for v in value ]
        elif type(value) is dict:
            self.__set__(instance, value.items())
        else:
            raise ExFieldInvalidTypeSet('To set a extended field, give a tuple with key'
                +' value, a list with KV tuples OR a dict')

        return value

    def _delete_field(self, instance, field):
        lang = translation.get_language()
        for tname, ttype in self._fields_tables.items():
            self.__ex_fields_class[tname].objects \
                .filter(fk=instance, field=field, lang=lang).delete()

    def _set_field(self, tname, instance, field, value):
        lang = translation.get_language()
        t = None
        try:
            t = self.__ex_fields_class[tname].objects.get(fk=instance, field=field, lang=lang)
        except self.__ex_fields_class[tname].DoesNotExist:
            t = self.__ex_fields_class[tname]()
            t.field = field
            t.fk = instance
            t.lang = lang
        except:#pragma:no cover
            raise

        t.value = value
        t.save()

    def __delete__(self, instance):#pragma:no cover
        if '__extendedFieldsCache' in instance.__dict__:
            del instance.__dict__.__extendedFieldsCache
