# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from tavi.documents import Document
from tavi import fields


class DocumentTest(unittest.TestCase):
    class Sample(Document):
        pass

    def test_sets_default_id(self):
        sample = self.Sample()
        self.assertEqual(None, sample.bson_id)

    def test_infers_collection_name(self):
        self.assertEqual("samples", self.Sample.collection_name)

    def test_has_a_collection(self):
        self.assertEqual(
            Collection(
                Database(MongoClient('localhost', 27017), 'test_database'),
                'samples'
            ),
            self.Sample.collection
        )

    def test_handles_false_boolean_field(self):
        class Target(Document):
            flag = fields.BooleanField("flag", default=True)

        t = Target()
        t.flag = False
        t.save()

        from_db = Target.find_all()[0]
        self.assertEqual(False, from_db.flag)
