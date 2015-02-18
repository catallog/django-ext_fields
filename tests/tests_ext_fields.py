# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.db import models
from ext_fields import *

@ExFieldsDecorator
class SimpleModel(models.Model):
    email = models.CharField(max_length=256)

class ExtFieldTestCase(TestCase):
    def setUp(self):
        SimpleModel.objects.create(email='lala@lele.com').ext_fields = {'asdf': 'fdsa', 'kkk': 10}
        SimpleModel.objects.create(email='lili@lele.com').ext_fields = {'asdf': 'sdfg', 'kkk': 11}
        SimpleModel.objects.create(email='lolo@lele.com').ext_fields = {'asdf': 'dfgh', 'kkk': 12}

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
