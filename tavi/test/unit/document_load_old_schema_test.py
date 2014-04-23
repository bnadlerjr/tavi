# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from tavi.documents import Document
from tavi import fields


class DocumentLoadOldSchemaTest(unittest.TestCase):
    """Tests the loading of data without fields which now exist in model"""
    class Sample(Document):
        first_name = fields.StringField("first_name", required=True)
        last_name = fields.StringField("last_name",  required=True)
        email = fields.StringField(
            "email",
            required=True,
            default="default email")

        address = fields.StringField("address", required=False)

    def setUp(self):
        super(DocumentLoadOldSchemaTest, self).setUp()
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']
        self.ids = self.db.samples.insert(
            [
                {"first_name": "John", "last_name": "Doe"},
                {"first_name": "Joe"},
            ]
        )

    def test_new_non_required_field(self):
        item = self.Sample.find_by_id(self.ids[0])
        self.assertEqual(None, item.address)
        self.assertEqual([], item.errors.full_messages)

    def test_new_required_field(self):
        item = self.Sample.find_by_id(self.ids[1])
        self.assertEqual(['Last Name is required'], item.errors.full_messages)

    def test_new_field_with_default(self):
        item = self.Sample.find_by_id(self.ids[0])
        self.assertEqual('default email', item.email)
