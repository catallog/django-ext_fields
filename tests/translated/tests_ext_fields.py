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
        a = SimpleModel.objects.create(email='my@pet.com')
        a.ext_fields = {'name': 'Tob', 'age': 15 , 'weight_uniti': 'Kg', 'weight': 22, 'color': 'Unknown', 'type': 'dog', 'breed': 'NA' }

        b = SimpleModel.objects.create(email='his@pet.com')
        b.ext_fields = {'name': 'James', 'age': 3, 'weight_uniti': 'Kg', 'weight': 1, 'color': 'Black', 'type': 'dog', 'breed': 'Pincher' }

        c = SimpleModel.objects.create(email='her@pet.com')
        c.ext_fields = {'name': 'Octopus', 'age': 1, 'weight_uniti': 'g', 'weight': 0.2 , 'color': 'Gray', 'type': 'spider', 'breed': 'Wolf' }


    def build_query(self, base):
        v = [
            ['string'], ['field', 'value']
        ]

        fields = [ 'simplemodelextendedfields%s__%s'%(a,b) for b in v[1] for a in v[0] ]

        base = base.values(*fields)

        print "-"*50
        print base.values(*fields).query
        print "-"*50

        return base

    def test_can_get_after_save(self):

        base = SimpleModel.objects.filter(email='my@pet.com')
        self.assertEqual(base.count(), 1)

        rqs = self.build_query(base)

        for i in self.build_query(base):
            print "\t>", i

        self.assertEqual(rqs.count(), 7)
