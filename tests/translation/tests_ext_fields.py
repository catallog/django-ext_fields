# -*- coding: utf-8 -*-
from django.test import TestCase

from .models import SimpleModel, SimpleNoTranslatedModel
from ext_fields.exceptions import ExFieldExceptionCannotSet
from ext_fields.exceptions import ExFieldInvalidTypeSet
from ext_fields.exceptions import ExFieldUnableSaveFieldType
from django.utils import translation
from django.conf import settings

import datetime


class ExtFieldTestCase(TestCase):
    def setUp(self):

        a = SimpleModel.objects.create(
            name='Anakin', planet='Tatooine')

        b = SimpleModel.objects.create(
            name='Boba', planet='Kamino')

        c = SimpleModel.objects.create(
            name='C3po', planet='Tatooine')

        d = SimpleModel.objects.create(
            name='Durge')

        e = SimpleNoTranslatedModel.objects.create(
            name='Chewbacca', planet='Kashyyyk')

        translation.activate('pt-br')
        a.ext_fields = {
            'name': 'Dart Vader',
            'planet': 'Terra',
            'race': 'Humano',
            'gender': 'Homen',
            'material': 'Midi-chlorian'
        }
        b.ext_fields = {
            'name': 'Boba Feet',
            'planet': 'Marte',
            'race': 'Humano',
            'gender': 'Homen',
            'material': 'Carbono'
        }

        translation.activate(settings.LANGUAGE_CODE)
        a.ext_fields = {
            'name': 'Dart Vader',
            'planet': 'Earth',
            'race': 'Human',
            'gender': 'Male',
            'age': 34,
            'weight': 79.5,
            'material': 'Midi-chlorian'
        }
        b.ext_fields = {
            'name': 'Boba Feet',
            'planet': 'Mars',
            'race': 'Human',
            'gender': 'Male',
            'age': 25,
            'weight': 72.2,
            'material': 'Carbon'
        }

        translation.activate('pt-br')
        c.ext_fields = {
            'name': 'C3po',
            'planet': 'Terra',
            'race': 'Andróide',
            'color': 'Ouro',
            'material': 'Aço'
        }
        d.ext_fields = {
            'name': 'Durge',
            'race': "Gen'Dai"
        }

        translation.activate(settings.LANGUAGE_CODE)
        c.ext_fields = {
            'name': 'C3po',
            'planet': 'Earth',
            'race': 'Droid',
            'age': 24,
            'weight': 153.5,
            'color': 'Gold',
            'material': 'Steel'
        }
        d.ext_fields = {
            'name': 'Durge',
            'race': "Gen'Dai",
            'age': 0.0
        }

        e.ext_fields = {
            'name': 'Chewie',
            'vehicle': 'Millenium Falcon'
        }

    def test_get_in_activated_language(self):

        a = SimpleModel.objects.filter(name='Anakin').last()
        b = SimpleModel.objects.filter(name='Boba').last()
        c = SimpleModel.objects.filter(name='C3po').last()
        d = SimpleModel.objects.filter(name='Durge').last()

        translation.activate(settings.LANGUAGE_CODE)
        self.assertEqual(a.ext_fields.get('race'), 'Human')
        self.assertEqual(b.ext_fields.get('race'), 'Human')
        self.assertEqual(c.ext_fields.get('race'), 'Droid')
        self.assertEqual(d.ext_fields.get('race'), "Gen'Dai")

        translation.activate('pt-br')
        self.assertEqual(a.ext_fields.get('race'), 'Humano')
        self.assertEqual(b.ext_fields.get('race'), 'Humano')
        self.assertEqual(c.ext_fields.get('race'), 'Andróide')
        self.assertEqual(d.ext_fields.get('race'), "Gen'Dai")
        self.assertEqual(d.ext_fields.get('age'), 0.0)

    def test_no_translated_model(self):
        a = SimpleNoTranslatedModel.objects.filter(name='Chewbacca').first()
        self.assertEqual(a.ext_fields.get('name'), 'Chewie')

    def test_translation_fallback(self):
        translation.deactivate_all()
        a = SimpleModel.objects.filter(name='Anakin').first()
        self.assertEqual(a.ext_fields.get('name'), 'Dart Vader')

        a.ext_fields = {'name': 'Anakin Skywalker'}

    def test_fallback_to_default_language(self):

        a = SimpleModel.objects.filter(name='Anakin').last()
        b = SimpleModel.objects.filter(name='Boba').last()
        c = SimpleModel.objects.filter(name='C3po').last()
        d = SimpleModel.objects.filter(name='Durge').last()

        translation.activate(settings.LANGUAGE_CODE)
        self.assertEqual(a.ext_fields.get('race'), 'Human')
        self.assertEqual(b.ext_fields.get('race'), 'Human')
        self.assertEqual(c.ext_fields.get('race'), 'Droid')
        self.assertEqual(d.ext_fields.get('race'), "Gen'Dai")

        translation.activate('es-es')
        self.assertEqual(a.ext_fields.get('race'), 'Human')
        self.assertEqual(b.ext_fields.get('race'), 'Human')
        self.assertEqual(c.ext_fields.get('race'), 'Droid')
        self.assertEqual(d.ext_fields.get('race'), "Gen'Dai")

    def test_filter_translated_field_value_defalt_lang(self):

        translation.activate(settings.LANGUAGE_CODE)
        humans = SimpleModel.ext_fields_manager.filter(race='Human').count()
        droids = SimpleModel.ext_fields_manager.filter(race='Droid').count()

        self.assertEqual(humans, 2)
        self.assertEqual(droids, 1)

    def test_filter_translated_field_value_selected_lang(self):

        translation.activate('pt-br')
        humans = SimpleModel.ext_fields_manager.filter(race='Humano').count()
        droids = SimpleModel.ext_fields_manager.filter(race='Andróide').count()

        self.assertEqual(humans, 2)
        self.assertEqual(droids, 1)

    def test_filter_translated_field_value_fallback_lang(self):

        translation.activate('es-es')
        humans = SimpleModel.ext_fields_manager.filter(race='Human').count()
        droids = SimpleModel.ext_fields_manager.filter(race='Droid').count()

        self.assertEqual(humans, 2)
        self.assertEqual(droids, 1)

    def test_distinctfields_default_lang(self):

        translation.activate(settings.LANGUAGE_CODE)
        dfields = SimpleModel.ext_fields_manager.distinct_fields()

        self.assertTrue('race' in dfields)
        self.assertTrue('gender' in dfields)
        self.assertTrue('color' in dfields)
        self.assertTrue('weight' in dfields)
        self.assertTrue('material' in dfields)
        self.assertTrue('age' in dfields)

    def test_distinctfields_selected_lang(self):

        translation.activate('pt-br')
        dfields = SimpleModel.ext_fields_manager.distinct_fields()

        self.assertTrue('race' in dfields)
        self.assertTrue('gender' in dfields)
        self.assertTrue('color' in dfields)
        self.assertTrue('weight' in dfields)
        self.assertTrue('material' in dfields)
        self.assertTrue('age' in dfields)

    def test_distinctfields_fallback_lang(self):

        translation.activate('es-es')
        dfields = SimpleModel.ext_fields_manager.distinct_fields()

        self.assertTrue('race' in dfields)
        self.assertTrue('gender' in dfields)
        self.assertTrue('color' in dfields)
        self.assertTrue('weight' in dfields)
        self.assertTrue('material' in dfields)
        self.assertTrue('age' in dfields)

    def test_have_option_in_default_lang(self):

        translation.activate(settings.LANGUAGE_CODE)
        has_race_count = SimpleModel.ext_fields_manager.filter(
            race__have=True).count()
        has_gender_count = SimpleModel.ext_fields_manager.filter(
            gender__have=True).count()
        has_color_count = SimpleModel.ext_fields_manager.filter(
            color__have=True).count()
        has_material_count = SimpleModel.ext_fields_manager.filter(
            material__have=True).count()

        self.assertEqual(has_race_count, 4)
        self.assertEqual(has_gender_count, 2)
        self.assertEqual(has_color_count, 1)
        self.assertEqual(has_material_count, 3)

    def test_have_option_in_selected_lang(self):

        translation.activate('pt-br')
        has_race_count = SimpleModel.ext_fields_manager.filter(
            race__have=True).count()
        has_gender_count = SimpleModel.ext_fields_manager.filter(
            gender__have=True).count()
        has_color_count = SimpleModel.ext_fields_manager.filter(
            color__have=True).count()
        has_material_count = SimpleModel.ext_fields_manager.filter(
            material__have=True).count()

        self.assertEqual(has_race_count, 4)
        self.assertEqual(has_gender_count, 2)
        self.assertEqual(has_color_count, 1)
        self.assertEqual(has_material_count, 3)

    def test_have_option_in_fallback_lang(self):

        translation.activate('es-es')
        has_race_count = SimpleModel.ext_fields_manager.filter(
            race__have=True).count()
        has_gender_count = SimpleModel.ext_fields_manager.filter(
            gender__have=True).count()
        has_color_count = SimpleModel.ext_fields_manager.filter(
            color__have=True).count()
        has_material_count = SimpleModel.ext_fields_manager.filter(
            material__have=True).count()

        self.assertEqual(has_race_count, 4)
        self.assertEqual(has_gender_count, 2)
        self.assertEqual(has_color_count, 1)
        self.assertEqual(has_material_count, 3)

    def test_other_field_lookups_default_language(self):

        translation.activate(settings.LANGUAGE_CODE)
        group_1 = SimpleModel.ext_fields_manager.filter(
            color__startswith='Go').values('name')
        group_2 = SimpleModel.ext_fields_manager.filter(
            material__endswith='n').values('name')
        group_3 = SimpleModel.ext_fields_manager.filter(
            material__contains='ee').values('name')
        group_4 = SimpleModel.ext_fields_manager.filter(
            material__icontains='Ee').values('name')
        group_5 = SimpleModel.ext_fields_manager.filter(
            race__regex='^[A-Za-z]+$'
        ).values('name')

        extvals = lambda n, s: list(map(lambda a: a.get(n), s))

        self.assertTrue('C3po' in extvals('name', group_1))
        self.assertTrue('Anakin' in extvals('name', group_2))
        self.assertTrue('Boba' in extvals('name', group_2))
        self.assertTrue('C3po' in extvals('name', group_3))
        self.assertTrue('C3po' in extvals('name', group_4))
        self.assertTrue('Anakin' in extvals('name', group_5))
        self.assertTrue('C3po' in extvals('name', group_5))
        self.assertTrue('Boba' in extvals('name', group_5))
        self.assertTrue('Durge' not in extvals('name', group_5))

    def test_asdict_im_default_lang(self):

        translation.activate(settings.LANGUAGE_CODE)
        a_n = SimpleModel.objects.filter(name='Anakin').last().as_dict()
        b_n = SimpleModel.objects.filter(name='Boba').last().as_dict()
        c_n = SimpleModel.objects.filter(name='C3po').last().as_dict()
        d_n = SimpleModel.objects.filter(name='Durge').last().as_dict()

        a_m = SimpleModel.objects.filter(name='Anakin').last().as_dict(True)
        b_m = SimpleModel.objects.filter(name='Boba').last().as_dict(True)
        c_m = SimpleModel.objects.filter(name='C3po').last().as_dict(True)
        d_m = SimpleModel.objects.filter(name='Durge').last().as_dict(True)

        self.assertEqual(a_n.get('name'), 'Anakin')
        self.assertEqual(a_n.get('planet'), 'Tatooine')
        self.assertEqual(b_n.get('name'), 'Boba')
        self.assertEqual(b_n.get('planet'), 'Kamino')
        self.assertEqual(c_n.get('name'), 'C3po')
        self.assertEqual(c_n.get('planet'), 'Tatooine')
        self.assertEqual(d_n.get('name'), 'Durge')
        self.assertEqual(d_n.get('planet'), None)

        self.assertEqual(a_m.get('name'), 'Dart Vader')
        self.assertEqual(a_m.get('planet'), 'Earth')
        self.assertEqual(b_m.get('name'), 'Boba Feet')
        self.assertEqual(b_m.get('planet'), 'Mars')
        self.assertEqual(c_m.get('name'), 'C3po')
        self.assertEqual(c_m.get('planet'), 'Earth')
        self.assertEqual(d_m.get('name'), 'Durge')
        self.assertEqual(d_m.get('planet'), None)

        self.assertEqual(a_n.get('age'), 34)
        self.assertEqual(b_n.get('age'), 25)
        self.assertEqual(c_n.get('age'), 24)
        self.assertEqual(d_n.get('age'), 0.0)

        self.assertEqual(a_n.get('weight'), 79.5)
        self.assertEqual(b_n.get('weight'), 72.2)
        self.assertEqual(c_n.get('weight'), 153.5)
        self.assertEqual(d_n.get('weight'), None)

    def test_asdict_im_selected_lang(self):

        translation.activate('pt-br')
        a_n = SimpleModel.objects.filter(name='Anakin').last().as_dict()
        b_n = SimpleModel.objects.filter(name='Boba').last().as_dict()
        c_n = SimpleModel.objects.filter(name='C3po').last().as_dict()
        d_n = SimpleModel.objects.filter(name='Durge').last().as_dict()

        a_m = SimpleModel.objects.filter(name='Anakin').last().as_dict(True)
        b_m = SimpleModel.objects.filter(name='Boba').last().as_dict(True)
        c_m = SimpleModel.objects.filter(name='C3po').last().as_dict(True)
        d_m = SimpleModel.objects.filter(name='Durge').last().as_dict(True)

        self.assertEqual(a_n.get('name'), 'Anakin')
        self.assertEqual(a_n.get('planet'), 'Tatooine')
        self.assertEqual(b_n.get('name'), 'Boba')
        self.assertEqual(b_n.get('planet'), 'Kamino')
        self.assertEqual(c_n.get('name'), 'C3po')
        self.assertEqual(c_n.get('planet'), 'Tatooine')
        self.assertEqual(d_n.get('name'), 'Durge')
        self.assertEqual(d_n.get('planet'), None)

        self.assertEqual(a_m.get('name'), 'Dart Vader')
        self.assertEqual(a_m.get('planet'), 'Terra')
        self.assertEqual(b_m.get('name'), 'Boba Feet')
        self.assertEqual(b_m.get('planet'), 'Marte')
        self.assertEqual(c_m.get('name'), 'C3po')
        self.assertEqual(c_m.get('planet'), 'Terra')
        self.assertEqual(d_m.get('name'), 'Durge')
        self.assertEqual(d_m.get('planet'), None)

        self.assertEqual(a_n.get('age'), 34)
        self.assertEqual(b_n.get('age'), 25)
        self.assertEqual(c_n.get('age'), 24)
        self.assertEqual(d_n.get('age'), 0.0)

        self.assertEqual(a_n.get('weight'), 79.5)
        self.assertEqual(b_n.get('weight'), 72.2)
        self.assertEqual(c_n.get('weight'), 153.5)
        self.assertEqual(d_n.get('weight'), None)

    def test_asdict_im_fallback_lang(self):

        translation.activate('es-es')
        a_n = SimpleModel.objects.filter(name='Anakin').last().as_dict()
        b_n = SimpleModel.objects.filter(name='Boba').last().as_dict()
        c_n = SimpleModel.objects.filter(name='C3po').last().as_dict()
        d_n = SimpleModel.objects.filter(name='Durge').last().as_dict()

        a_m = SimpleModel.objects.filter(name='Anakin').last().as_dict(True)
        b_m = SimpleModel.objects.filter(name='Boba').last().as_dict(True)
        c_m = SimpleModel.objects.filter(name='C3po').last().as_dict(True)
        d_m = SimpleModel.objects.filter(name='Durge').last().as_dict(True)

        self.assertEqual(a_n.get('name'), 'Anakin')
        self.assertEqual(a_n.get('planet'), 'Tatooine')
        self.assertEqual(b_n.get('name'), 'Boba')
        self.assertEqual(b_n.get('planet'), 'Kamino')
        self.assertEqual(c_n.get('name'), 'C3po')
        self.assertEqual(c_n.get('planet'), 'Tatooine')
        self.assertEqual(d_n.get('name'), 'Durge')
        self.assertEqual(d_n.get('planet'), None)

        self.assertEqual(a_m.get('name'), 'Dart Vader')
        self.assertEqual(a_m.get('planet'), 'Earth')
        self.assertEqual(b_m.get('name'), 'Boba Feet')
        self.assertEqual(b_m.get('planet'), 'Mars')
        self.assertEqual(c_m.get('name'), 'C3po')
        self.assertEqual(c_m.get('planet'), 'Earth')
        self.assertEqual(d_m.get('name'), 'Durge')
        self.assertEqual(d_m.get('planet'), None)

        self.assertEqual(a_n.get('age'), 34)
        self.assertEqual(b_n.get('age'), 25)
        self.assertEqual(c_n.get('age'), 24)
        self.assertEqual(d_n.get('age'), 0.0)

        self.assertEqual(a_n.get('weight'), 79.5)
        self.assertEqual(b_n.get('weight'), 72.2)
        self.assertEqual(c_n.get('weight'), 153.5)
        self.assertEqual(d_n.get('weight'), None)

    def test_deletion(self):
        a = SimpleModel.objects.get(name='Anakin')
        b = SimpleModel.objects.get(name='Boba')

        a.ext_fields = {'material': None}
        b.ext_fields = {'race': None}

        a = SimpleModel.objects.get(name='Anakin')
        b = SimpleModel.objects.get(name='Boba')

        self.assertFalse('material' in a.ext_fields.keys())
        self.assertFalse('race' in b.ext_fields.keys())

    def test_descriptors(self):

        mod = SimpleModel.objects.get(name='Anakin')

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

        try:
            SimpleModel.ext_fields_manager.filter(color__startswith=False)
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldUnableSaveFieldType)

        mod = SimpleModel.objects.get(name='Boba')
        try:
            mod.ext_fields_manager = object()
        except Exception, ex:
            self.assertIsInstance(ex, ExFieldExceptionCannotSet)

    def test_exclusion(self):

        self.assertEqual(
            SimpleModel.ext_fields_manager.exclude(name='C3po').count(), 3
        )

    def test_date_detect(self):
        mod = SimpleModel.objects.get(name='Anakin')
        mod.ext_fields = {'date': '2015-10-28T11:23:47.311Z'}
        self.assertEqual(type(mod.ext_fields.get('date')), datetime.datetime)
