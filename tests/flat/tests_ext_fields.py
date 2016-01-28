# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from .models import SimpleModel
from ext_fields.exceptions import ExFieldExceptionCannotDel
from ext_fields.exceptions import ExFieldExceptionCannotSet
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType


class ExtFieldTestCase(TestCase):
    def setUp(self):
        SimpleModel.objects.create(email='lala@lele.com').ext_fields = {'asdf': 'fdsa', 'kkk': 10, 'hhh': 3, 'lll': '=)'}
        SimpleModel.objects.create(email='lili@lele.com').ext_fields = {'asdf': 'sdfg', 'kkk': 11, 'hhh': 4}
        SimpleModel.objects.create(email='lolo@lele.com').ext_fields = {'asdf': 'dfgh', 'kkk': 12, 'lll': '=)'}
        SimpleModel.objects.create(email='email@model.com').ext_fields = {'email': 'email@ext.com', 'name': 'Mail E.'}


    def test_can_get_after_save(self):
        """Check if load is ok"""
        k = SimpleModel.objects.get(email='lala@lele.com').ext_fields
        k = SimpleModel.objects.get(email='lala@lele.com').ext_fields
        self.assertEqual('asdf' in k, True)
        self.assertEqual(k['asdf'], 'fdsa')
        self.assertEqual('kkk' in k, True)
        self.assertEqual(k['kkk'], 10)

        k = SimpleModel.objects.get(email='lili@lele.com').ext_fields
        self.assertEqual('asdf' in k, True)
        self.assertEqual(k['asdf'], 'sdfg')
        self.assertEqual('kkk' in k, True)
        self.assertEqual(k['kkk'], 11)

        k = SimpleModel.objects.get(email='lolo@lele.com').ext_fields
        self.assertEqual('asdf' in k, True)
        self.assertEqual(k['asdf'], 'dfgh')
        self.assertEqual('kkk' in k, True)
        self.assertEqual(k['kkk'], 12)

    def test_correctly_updates(self):
        """check if fields will be correctly updated"""
        k10 = SimpleModel.ext_fields_manager.filter(kkk=10)[0]
        k11 = SimpleModel.ext_fields_manager.filter(kkk=11)[0]
        k12 = SimpleModel.ext_fields_manager.filter(kkk=12)[0]

        k10.ext_fields = {'asdf': 'test1', 'kkk': 'test2'}
        k11.ext_fields = {'asdf': None}
        k11.ext_fields = {'asdf': 11}
        k12.ext_fields = {'kkk': None}
        k12.ext_fields = {'kkk': 'test4'}

        k10 = SimpleModel.objects.filter(email='lala@lele.com')[0].ext_fields
        k11 = SimpleModel.objects.filter(email='lili@lele.com')[0].ext_fields
        k12 = SimpleModel.objects.filter(email='lolo@lele.com')[0].ext_fields

        self.assertEqual(k10['asdf'], 'test1')
        self.assertEqual(k10['kkk'], 'test2')

        self.assertEqual(k11['asdf'], 11)
        self.assertEqual(k11['kkk'], 11)

        self.assertEqual(k12['asdf'], 'dfgh')
        self.assertEqual(k12['kkk'], 'test4')

    def test_selects(self):
        """check if select is working"""
        k = SimpleModel.ext_fields_manager.filter(asdf='fdsa').values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lala@lele.com')

        k = SimpleModel.ext_fields_manager.filter(asdf='dfgh').values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lolo@lele.com')

        k = SimpleModel.ext_fields_manager.filter(
            queryset=SimpleModel.objects.filter(email='lili@lele.com'),
            kkk=11
        ).values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lili@lele.com')

        k = SimpleModel.ext_fields_manager.filter(
            queryset=SimpleModel.objects.filter(email='lili@lele.com'),
            kkk=12
        ).values('email')
        self.assertEqual(len(k), 0)

    def test_distinct_fields(self):
        """check if can get name of distinct fields correctly"""
        dfields = SimpleModel.ext_fields_manager.distinct_fields()

        self.assertEqual(len(dfields), 6)
        self.assertEqual('asdf' in dfields, True)
        self.assertEqual('hhh' in dfields, True)
        self.assertEqual('lll' in dfields, True)
        self.assertEqual('kkk' in dfields, True)
        self.assertEqual('name' in dfields, True)
        self.assertEqual('email' in dfields, True)

    def test_have_opt(self):
        """check if will correctly return the have filter"""
        k = SimpleModel.ext_fields_manager.filter(asdf__have=True)#.values('email')
        self.assertEqual(len(k), 3)

        k = SimpleModel.ext_fields_manager.filter(asdf__have=False).values('email')
        self.assertEqual(len(k), 1)

        k = SimpleModel.ext_fields_manager.filter(hhh__have=True).values('email')
        self.assertEqual(len(k), 2)

        k = SimpleModel.ext_fields_manager.filter(hhh__have=False).values('email')
        self.assertEqual(len(k), 2)

        k = SimpleModel.ext_fields_manager.filter(lll__have=True).values('email')
        self.assertEqual(len(k), 2)

        k = SimpleModel.ext_fields_manager.filter(lll__have=False).values('email')
        self.assertEqual(len(k), 2)

    def test_extended_opt(self):
        """check if especial options will work"""
        k = SimpleModel.ext_fields_manager.filter(asdf__exact='fdsa').values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lala@lele.com')

        k = SimpleModel.ext_fields_manager.filter(asdf__startswith='df').values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lolo@lele.com')

        k = SimpleModel.ext_fields_manager.filter(asdf__endswith='gh').values('email')
        self.assertEqual(len(k), 1)
        self.assertEqual('email' in k[0], True)
        self.assertEqual(k[0]['email'], 'lolo@lele.com')

        k = SimpleModel.ext_fields_manager.filter(kkk__gte=11).values('email')
        self.assertEqual(len(k), 2)

    def test_deletes(self):
        """check if it is able to delete fields on tables"""
        k10 = SimpleModel.ext_fields_manager.filter(kkk=10)[0]
        k11 = SimpleModel.ext_fields_manager.filter(kkk=11)[0]
        k12 = SimpleModel.ext_fields_manager.filter(kkk=12)[0]

        k10.ext_fields = {'asdf': None, 'kkk': None}
        k11.ext_fields = {'asdf': None}
        k12.ext_fields = {'kkk': None}

        k10 = SimpleModel.objects.filter(email='lala@lele.com')[0].ext_fields
        k11 = SimpleModel.objects.filter(email='lili@lele.com')[0].ext_fields
        k12 = SimpleModel.objects.filter(email='lolo@lele.com')[0].ext_fields

        self.assertEqual('asdf' in k10, False)
        self.assertEqual('kkk' in k10, False)

        self.assertEqual('asdf' in k11, False)
        self.assertEqual('kkk' in k11, True)

        self.assertEqual('asdf' in k12, True)
        self.assertEqual('kkk' in k12, False)


    def test_serializers_helpers(self):

        mod = SimpleModel.objects.get(email='email@model.com')

        self.assertEqual(mod.email, 'email@model.com')

        self.assertEqual(mod.as_dict().get('email'), 'email@model.com')
        self.assertEqual(mod.as_dict().get('name'), 'Mail E.')

        self.assertEqual(mod.as_dict(False).get('email'), 'email@model.com')
        self.assertEqual(mod.as_dict(False).get('name'), 'Mail E.')

        self.assertEqual(mod.as_dict(True).get('email'), 'email@ext.com')
        self.assertEqual(mod.as_dict(True).get('name'), 'Mail E.')

        self.assertEqual(mod.ext_fields_data.get('email'), 'email@ext.com')
        self.assertEqual(mod.ext_fields_data.get('name'), 'Mail E.')

    def test_descriptors(self):

        mod = SimpleModel.objects.get(email='email@model.com')

        try:
            mod.ext_fields = ('test', 'test_val', 'out of bounds',)
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldInvalidTypeSet)

        try:
            mod.ext_fields = (1, 'Incompatible key',)
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldInvalidTypeSet)

        try:
            mod.ext_fields = 5.67
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldInvalidTypeSet)

        try:
            mod.ext_fields = ('key', object(),)
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldUnableSaveFieldType)

    def test_manager_exceptions(self):

        s = str('mail')
        try:
            a = SimpleModel.ext_fields_manager.filter(email__startswith=False)
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldUnableSaveFieldType)

        mod = SimpleModel.objects.get(email='email@model.com')


        try:
            mod.ext_fields_manager = object()
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldExceptionCannotSet)

    def test_exclusion(self):

        self.assertEqual(
            SimpleModel.ext_fields_manager.exclude(name='Mail E.').count(), 3
        )

    def test_implicit_type_cast(self):

        mod = SimpleModel.objects.get(email='email@model.com')

        mod.ext_fields = { 'area': 'outside hall'}
        self.assertTrue( type(mod.ext_fields.get('area')) in [str, unicode])

        mod.ext_fields = { 'area': 34}
        self.assertEqual(type(mod.ext_fields.get('area')),int)

        mod.ext_fields = { 'area': 33.98 }
        self.assertEqual(type(mod.ext_fields.get('area')),float)
