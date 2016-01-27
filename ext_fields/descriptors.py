# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:51:16
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from ext_fields.mapper import Mapper


class ExFieldsDescriptors(Mapper):

    def __get__(self, instance, owner):
        if '__extFielCache' not in instance.__dict__:
            instance.__extFielCache = dict()
            res = self.model_class.objects.filter(fk=instance.pk).all()
            for row in res:
                instance.__extFielCache[row.field] = self.get_row_value(row)
        return instance.__extFielCache

    def __set__(self, instance, value):
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
            self._set_field(instance, value[0], value[1])

        elif type(value) is list:
            [ self.__set__(instance, v) for v in value ]
        elif type(value) is dict:
            self.__set__(instance, value.items())
        else:
            raise ExFieldInvalidTypeSet('To set a extended field, give a tuple with key'
                +' value, a list with KV tuples OR a dict')
        return value

    def _delete_field(self, instance, field):
        self.model_class.objects.filter(fk=instance, field=field).delete()

    def _set_field(self, instance, field, value):
        if self.get_value_map(value):
            self.model_class.objects.update_or_create(
                fk=instance, field=field,
                defaults=self.get_dict_val(value)
            )
        else:
            raise ExFieldUnableSaveFieldType('for now only str, int, float and datetime'
                    +'can be used as extended fields')

    def __delete__(self, instance):#pragma:no cover
        if '__extFielCache' in instance.__dict__:
            del instance.__dict__.__extFielCache
