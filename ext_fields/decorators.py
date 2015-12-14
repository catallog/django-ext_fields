# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 09:52:12
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from .descriptors import ExFieldsDescriptors
from .helpers import as_dict
from .helpers import create_ex_fields_parent
from .managers import ExFieldsManager
from datetime import datetime
from django.db import models


class EmptyMeta:
    pass


def ExFieldsDecorator(cls):

    defaults_common = {'__module__': cls.__module__}
    defaults_common['Meta'] = cls.Meta if hasattr(cls, 'Meta') else EmptyMeta

    name_base = cls.__name__ + 'ExtendedFields'
    fields_tables = {
        name_base+'String':  (unicode,  models.CharField, {'null':False, 'max_length':256},),
        name_base+'Integer': (int,      models.IntegerField, {'null':False},),
        name_base+'Float':   (float,    models.FloatField, {'null':False},),
        name_base+'Date':    (datetime, models.DateTimeField, {'null':False},)
    }
    fields_models = dict()
    for k, v in fields_tables.items():
        prop = {'value': v[1](**(v[2]))}
        prop.update(defaults_common)
        fields_models[k] = type(str(k), (create_ex_fields_parent(cls),), prop)

    cls.ext_fields = ExFieldsDescriptors(fields_tables, fields_models)
    cls.ext_fields_manager = ExFieldsManager(fields_tables, fields_models)
    cls.__ex_fields_class = fields_models
    setattr(cls, 'as_dict', as_dict )

    return cls
