# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from tavi.documents import Document
from tavi import fields


class DocumentFindTest(unittest.TestCase):
    class Sample(Document):
        first_name = fields.StringField("first_name", required=True)
        last_name = fields.StringField("last_name",  required=True)

    def setUp(self):
        super(DocumentFindTest, self).setUp()
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']
        self.ids = self.db.samples.insert(
            [
                {"first_name": "John", "last_name": "Doe"},
                {"first_name": "Joe",  "last_name": "Smith"},
                {"first_name": "John", "last_name": "Smith"}
            ]
        )

        self.assertEqual(3, self.db.samples.count())

    def test_find_one(self):
        result = self.Sample.find_one(self.ids[0])
        self.assertEqual("John", result.first_name)
        self.assertEqual(self.ids[0], result.bson_id)

    def test_find_one_does_not_find_any(self):
        self.assertIsNone(self.Sample.find_one({"first_name": "No such name"}))

    def test_find_by_id_using_bson_id(self):
        result = self.Sample.find_by_id(self.ids[1])
        self.assertEqual("Joe", result.first_name)
        self.assertEqual(self.ids[1], result.bson_id)

    def test_find_by_id_using_string_id(self):
        result = self.Sample.find_by_id(str(self.ids[1]))
        self.assertEqual("Joe", result.first_name)
        self.assertEqual(self.ids[1], result.bson_id)

    def test_find(self):
        result = self.Sample.find({"last_name": "Smith"})
        self.assertEqual(2, len(result))
        self.assertEqual("Smith", result[0].last_name)
        self.assertEqual("Smith", result[1].last_name)

        self.assertEqual(self.ids[1], result[0]._id)
        self.assertEqual(self.ids[2], result[1]._id)

    def test_find_all(self):
        result = self.Sample.find_all()
        self.assertEqual(3, len(result))

    def test_find_all_when_collection_is_empty(self):
        self.db.drop_collection("samples")
        self.assertEqual([], self.Sample.find_all())

    def test_count(self):
        self.assertEqual(3, self.Sample.count())
