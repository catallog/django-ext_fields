# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import SimpleModel
from django.test import TestCase
from django.utils import translation
from django.conf import settings
from ext_fields.exceptions import ExFieldExceptionCannotDel
from ext_fields.exceptions import ExFieldExceptionCannotSet
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from django.db import connection


class ExtFieldTestCase(TestCase):
    def setUp(self):
        translation.activate(settings.LANGUAGE_CODE)
        a = SimpleModel.objects.create(email='my@pet.com')
        a.ext_fields = {'name': 'Tob', 'age': 15 , 'weight_uniti': 'Kg', 'weight': 22, 'color': 'Unknown', 'type': 'dog', 'breed': 'NA' }
        translation.activate('pt')
        a.ext_fields = {'name': 'Totó', 'age': 15 , 'weight_uniti': 'Kg', 'weight': 22, 'color': 'Desconhecida', 'type': 'Cachorro', 'breed': 'NA' }

        translation.activate('pt')
        b = SimpleModel.objects.create(email='his@pet.com')
        b.ext_fields = {'name': 'João', 'age': 3, 'weight_uniti': 'Kg', 'weight': 1, 'color': 'Preto', 'type': 'Cachorro', 'breed': 'Pequenes' }
        translation.activate(settings.LANGUAGE_CODE)
        b.ext_fields = {'name': 'James', 'age': 3, 'weight_uniti': 'Kg', 'weight': 1, 'color': 'Black', 'type': 'dog', 'breed': 'Pincher' }

        translation.activate(settings.LANGUAGE_CODE)
        c = SimpleModel.objects.create(email='her@pet.com')
        c.ext_fields = {'name': 'Octopus', 'age': 1, 'weight_uniti': 'g', 'weight': 0.2 , 'color': 'Gray', 'type': 'spider', 'breed': 'Wolf' }
        translation.activate('pt')
        c.ext_fields = {'name': 'Otávio', 'age': 1, 'weight_uniti': 'g', 'weight': 0.2 , 'color': 'Cinza', 'type': 'aranha', 'breed': 'Lobo' }

        translation.activate('es')
        c.ext_fields = {'name': 'Octavio', 'age': 10, 'color': 'Gris' }

    def test_basic_descriptor_test(self):

        translation.activate(settings.LANGUAGE_CODE)
        a = SimpleModel.objects.get(email='my@pet.com').ext_fields
        b = SimpleModel.objects.get(email='his@pet.com').ext_fields
        c = SimpleModel.objects.get(email='her@pet.com').ext_fields

        self.assertEqual(a.get('name'), 'Tob')
        self.assertEqual(b.get('name'), 'James')
        self.assertEqual(c.get('name'), 'Octopus')
        self.assertEqual(a.get('color'), 'Unknown')
        self.assertEqual(b.get('color'), 'Black')
        self.assertEqual(c.get('color'), 'Gray')
        self.assertEqual(a.get('age'), 15)
        self.assertEqual(b.get('age'), 3)
        self.assertEqual(c.get('age'), 1)

        translation.activate('pt')
        a = SimpleModel.objects.get(email='my@pet.com').ext_fields
        b = SimpleModel.objects.get(email='his@pet.com').ext_fields
        c = SimpleModel.objects.get(email='her@pet.com').ext_fields

        self.assertEqual(a.get('name'), 'Totó')
        self.assertEqual(b.get('name'), 'João')
        self.assertEqual(c.get('name'), 'Otávio')
        self.assertEqual(a.get('color'), 'Desconhecida')
        self.assertEqual(b.get('color'), 'Preto')
        self.assertEqual(c.get('color'), 'Cinza')
        self.assertEqual(a.get('age'), 15)
        self.assertEqual(b.get('age'), 3)
        self.assertEqual(c.get('age'), 1)

        translation.activate('es')
        a = SimpleModel.objects.get(email='my@pet.com').ext_fields
        c = SimpleModel.objects.get(email='her@pet.com').ext_fields
        self.assertEqual(a.get('name'), 'Tob')
        self.assertEqual(c.get('name'), 'Octavio')
        self.assertEqual(a.get('color'), 'Unknown')
        self.assertEqual(c.get('color'), 'Gris')
        self.assertEqual(a.get('age'), 15)
        self.assertEqual(b.get('age'), 3)
        self.assertEqual(c.get('age'), 10)
