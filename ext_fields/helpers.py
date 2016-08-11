# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:34:48
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from django.db import models
from ext_fields import constants


def create_ex_fields_parent(cls):
    class ExtendedFieldsParent(models.Model):
        fk = models.ForeignKey(cls, null=False)
        field = models.CharField(max_length=128, null=False)
        lang = models.CharField(max_length=5, null=True, blank=True, default=None)
        value_str = models.TextField(null=True, blank=True, default=None)
        value_int = models.IntegerField(null=True, blank=True, default=None)
        value_float = models.FloatField(null=True, blank=True, default=None)
        value_date = models.DateTimeField(null=True, blank=True, default=None)

        class Meta:
            abstract = True
            unique_together = (('field', 'fk',),)
            index_together = ('field', 'fk',)

        @property
        def value(self):
            def nonempty(a, b):
                return a or getattr(self, constants.VALUE_PREFIX + b, None)
            return reduce(nonempty, constants.TYPEMAP.keys(), None)

    return ExtendedFieldsParent


def as_dict(self, override=False):
    def __get_ext_fields_dicts__(ovr):
        model_fields = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        if ovr:
            return model_fields, self.ext_fields
        return self.ext_fields, model_fields
    base, ext = __get_ext_fields_dicts__(override)
    base.update(ext)
    return base
