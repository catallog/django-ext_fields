# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 08:56:05
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/
from django.db import models
from ext_fields.decorators import ExFieldsDecorator


@ExFieldsDecorator
class SimpleModel(models.Model):
    name = models.CharField(max_length=128, null=False)
    planet = models.CharField(max_length=128, null=True, blank=True, default=None)


@ExFieldsDecorator
class SimpleNoTranslatedModel(models.Model):
    name = models.CharField(max_length=128, null=False)
    planet = models.CharField(max_length=128, null=True, blank=True, default=None)
