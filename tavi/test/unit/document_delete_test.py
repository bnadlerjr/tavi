# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from tavi.documents import Document
from tavi import fields


class DocumentDeleteTest(unittest.TestCase):
    class Sample(Document):
        name = fields.StringField("name", required=True)

    def test_successful_delete(self):
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']

        sample = self.Sample()
        sample.name = "John"
        sample.save()

        self.assertEqual(1, self.db.samples.count())
        sample.delete()
        self.assertEqual(0, self.db.samples.count())
