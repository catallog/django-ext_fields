# -*- coding: utf-8 -*-
# @Date    : 2016-10-24 10:00:00
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/
from django import forms
from django.contrib import admin

from ext_fields.mapper import Mapper

import ast


class ExtFieldsForm(forms.ModelForm):

    value = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ExtFieldsForm, self).__init__(*args, **kwargs)

        try:
            instance = kwargs.get('instance', None)
            if instance:
                self.initial['value'] = instance.value
                self.initial.update()
        except:
            import traceback
            traceback.print_exc()

    def save(self, *args, **kwargs):
        a = super(ExtFieldsForm, self).save(*args, **kwargs)

        ext_value = self.cleaned_data.pop('value', None)
        try:
            val = ast.literal_eval(ext_value)
        except Exception:
            val = ext_value

        rows = Mapper.get_dict_val(val)
        for field, value in rows.items():
            setattr(a, field, value)
        a.save()
        return a


def extFieldAdminFactory(baseclass):
    class ExtFieldsAdmin(baseclass):
        classes = ('collapse',)
        extra = 0
        form = ExtFieldsForm
        fields = ('field', 'value',)
        readonly_fields = ('field',)

        def value(self, obj):
            return obj.value
        value.short_description = 'Value'

        def get_language(self, request):
            return None

        def get_queryset(self, request):
            qs = super(ExtFieldsAdmin, self).get_queryset(request)
            lang = self.get_language(request)
            if lang:
                qs = qs.filter(lang=lang)
            return qs
    return ExtFieldsAdmin

ExtFieldsTabularInline = extFieldAdminFactory(admin.TabularInline)
ExtFieldsStackedInline = extFieldAdminFactory(admin.StackedInline)
