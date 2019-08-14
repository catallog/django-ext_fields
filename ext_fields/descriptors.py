# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:51:16
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/
from django.conf import settings
from django.db.models import Q
from django.utils import translation
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from ext_fields.mapper import Mapper


TRANSLATE = getattr(settings, "EXTFIELDS_TRANSLATE", False)
FALLBACK_TRANSLATE = getattr(settings, "EXTFIELDS_FALLBACK_TRANSLATE", False)


class ExFieldsDescriptors(Mapper):

    def __get__(self, instance, owner):
        if not instance:  # pragma:no cover
            return None

        if '__extFielCache' not in instance.__dict__:
            instance.__extFielCache = dict()

            if TRANSLATE and self.translated:
                lang = translation.get_language()
                is_default_lang = False
                if lang and hasattr(settings, 'LANGUAGE_CODE'):
                    lang_code = settings.LANGUAGE_CODE.lower()
                    is_default_lang = lang.lower() == lang_code

                if FALLBACK_TRANSLATE and not is_default_lang:
                    res = self.model_class.objects.filter(
                        fk=instance.pk
                    ).filter(
                        Q(lang=lang) | Q(lang=settings.LANGUAGE_CODE)
                    ).all()
                    res = sorted(res, lambda a, b: 0 if a == b else -1 if a == settings.LANGUAGE_CODE else 1, lambda x: x.lang)
                else:
                    res = self.model_class.objects.filter(
                        fk=instance.pk, lang=lang).all()
            else:
                res = self.model_class.objects.filter(fk=instance.pk).all()

            for row in res:
                instance.__extFielCache[row.field] = self.get_row_value(row)
        return instance.__extFielCache

    def __set__(self, instance, value):
        if (type(value) is tuple):
            if len(value) is not 2:
                raise ExFieldInvalidTypeSet(
                    'on setting ext_fields: Invalid lenght'
                    ' for tuple, len(value) must be 2,'
                    ' first item with key, second'
                    ' the holder value')
            if type(value[0]) not in (str,):
                raise ExFieldInvalidTypeSet(
                    'on setting ext_fields, first field on '
                    'property tuple must be str with field name')

            if value[1] is None:
                return self._delete_field(instance, value[0])
            self._set_field(instance, value[0], value[1])

        elif type(value) is list:
            [self.__set__(instance, v) for v in value]
        elif type(value) is dict:
            self.__set__(instance, list(value.items()))
        else:
            raise ExFieldInvalidTypeSet(
                'To set a extended field, give a tuple with key'
                ' value, a list with KV tuples OR a dict')
        return value

    def _delete_field(self, instance, field):
        params = {'fk': instance, 'field': field}
        self.model_class.objects.filter(**params).delete()

    def _set_field(self, instance, field, value):
        if self.get_value_map(value):
            params = {
                'fk': instance,
                'field': field,
                'defaults': self.get_dict_val(value)
            }

            if TRANSLATE and self.translated:
                lang = translation.get_language()
                if not lang and FALLBACK_TRANSLATE:
                    lang = settings.LANGUAGE_CODE
                params['lang'] = lang

            self.model_class.objects.update_or_create(**params)
        else:
            raise ExFieldUnableSaveFieldType(
                'for now only str, int, float and datetime'
                'can be used as extended fields'
            )

    def __delete__(self, instance):  # pragma:no cover
        if '__extFielCache' in instance.__dict__:
            del instance.__dict__.__extFielCache
