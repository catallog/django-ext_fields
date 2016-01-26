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

    ext_table_name = cls.__name__ + 'ExtFields'

    model_class = type(str(ext_table_name), (create_ex_fields_parent(cls),), defaults_common)

    cls.ext_fields = ExFieldsDescriptors(model_class)
    cls.ext_fields_manager = ExFieldsManager(model_class)
    cls.__ex_fields_class = model_class
    cls.as_dict = as_dict
    cls.ext_fields_data = property(lambda instance: instance.ext_fields)

    return cls
