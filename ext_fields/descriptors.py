# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:51:16
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from datetime import datetime

class ExFieldsDescriptors(object):

    typemap = {
        'int': [ int ],
        'str': [ str, unicode ],
        'float': [ float ],
        'date': [ datetime ]
    }

    def __init__(self, model_class):
        self.__ex_fields_class = model_class

    def is_supported(self, value):
        last_valid_match = lambda a,b: a or type(value) in b
        return reduce(last_valid_match, self.typemap.values(), False)

    def get_row_value(self, row):
        last_nonempty_field = lambda a, b: a or getattr(row, 'value_%s' % b)
        return reduce(last_nonempty_field, self.typemap.keys(), None)

    def __get__(self, instance, owner):
        if '__extFielCache' not in instance.__dict__:
            instance.__extFielCache = dict()

            res = self.__ex_fields_class.objects.filter(fk=instance.pk).all()
            for row in res:
                instance.__extFielCache[row.field] = self.get_row_value(row)
        return instance.__extFielCache

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
        self.__ex_fields_class.objects.filter(fk=instance, field=field).delete()

    def _set_field(self, instance, field, value):
        if self.is_supported(value):
            vt = type(value)
            upd = { 'value_%s' % k : value if vt in v else None for k,v in self.typemap.items() }
            try:
                self.__ex_fields_class.objects.update_or_create(
                    fk=instance, field=field, defaults=upd
                )
            except Exception, e:
                raise e
        else:
            raise ExFieldUnableSaveFieldType('for now only str, int, float and datetime'
                    +'can be used as extended fields')


    def __delete__(self, instance):#pragma:no cover
        if '__extFielCache' in instance.__dict__:
            del instance.__dict__.__extFielCache
