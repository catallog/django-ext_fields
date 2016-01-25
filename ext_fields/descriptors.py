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
from django.db import connection


class ExFieldsDescriptors(object):
    def __init__(self, fields_tables, fields_models):
        self._fields_tables = fields_tables
        self.__ex_fields_class = fields_models

    def _get_new_queryset(self, owner):
        subs = []
        count = 0
        app_alias = owner._meta.db_table.split('_')[0]
        for k in self._fields_tables.keys():
            values = []
            for c in range(len(self._fields_tables.keys())):
                if c==count:
                    values.append("VALUE AS val%d"%c)
                else:
                    values.append("NULL AS val%d"%c)
            count += 1

            table = app_alias + '_' + k.lower()
            subs.append(
                "SELECT field, fk_id, lang, " + ','.join(values) + " FROM {}".format(table)
            )
        core = ' UNION ALL '.join(subs)
        q = "SELECT * FROM ({}) WHERE fk_id = %s AND lang = %s".format(core)
        return q

    def __get__(self, instance, owner):

        if '__extendedFieldsCache' not in instance.__dict__:
            instance.__extendedFieldsCache = dict()

            cursor = connection.cursor()
            cursor.execute(
                self._get_new_queryset(owner),
                [
                    instance.pk,
                    translation.get_language()
                ]
            )

            for r in cursor.fetchall():
                instance.__extendedFieldsCache[r[0]] = reduce(lambda a,b: a or b, r[3:])

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
