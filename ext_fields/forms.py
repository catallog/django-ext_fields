# -*- coding: utf-8 -*-
# @Date    : 2016-05-04 17:41:48
# @Author  : Rafael Fernandes (basask@collabo.com.br)
# @Link    : http://www.collabo.com.br/

from __future__ import unicode_literals

from django import forms
from django.forms import widgets


class ExtFieldsWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            widgets.TextInput(attrs=attrs),
            widgets.TextInput(attrs=attrs),
        )
        super(ExtFieldsWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.key, value.value]
        return [None, None]

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        values = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            ret = dict()
            ret[values[0]] = values[1]
        except ValueError:
            return ''
        else:
            return ret


class ExtFieldsField(forms.Field):

    widget = ExtFieldsWidget

    def to_python(self, value):
        return super(ExtFieldsField, self).to_python(value)
