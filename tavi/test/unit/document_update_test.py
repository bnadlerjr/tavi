# -*- coding: utf-8 -*-
import unittest
from pymongo import MongoClient
from tavi.documents import EmbeddedDocument, Document
from tavi import fields


class Address(EmbeddedDocument):
    street = fields.StringField("street")
    created_at = fields.DateTimeField("created_at")
    last_modified_at = fields.DateTimeField("last_modified_at")


class DocumentUpdateTest(unittest.TestCase):
    class Sample(Document):
        name = fields.StringField("name", required=True, unique=True)
        created_at = fields.DateTimeField("created_at")
        last_modified_at = fields.DateTimeField("last_modified_at")
        address = fields.EmbeddedField("address", Address)
        status = fields.StringField("my_status")

    def setUp(self):
        super(DocumentUpdateTest, self).setUp()
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']
        self.sample = self.Sample()

    def test_does_not_set_created_at(self):
        self.sample.name = "John"
        assert self.sample.save(), self.sample.errors.full_messages
        created_at = self.sample.created_at
        self.assertIsNotNone(created_at)

        self.sample.name = "Paul"
        assert self.sample.save(), self.sample.errors.full_messages

        self.assertEqual(created_at, self.sample.created_at)

    def test_uses_mongo_field_names(self):
        self.sample.name = "John"
        self.sample.status = "active"
        self.sample.save()

        self.sample.status = "inactive"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("inactive", actual['my_status'])

    def test_updates_existing_documents(self):
        self.sample.name = "John"
        self.sample.save()

        self.sample.name = "Joe"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("Joe", actual['name'])

    def test_sets_last_modified_if_present(self):
        self.sample.name = "John"
        self.sample.save()
        last_modified = self.sample.last_modified_at
        self.assertIsNotNone(last_modified)

        self.sample.name = "Joe"
        self.sample.save()
        self.assertNotEqual(last_modified, self.sample.last_modified_at)

    def test_sets_last_modified_for_any_embedded_documents(self):
        self.sample.name = "John"
        self.sample.address = Address()
        self.assertTrue(self.sample.save(), self.sample.errors.full_messages)
        last_modified = self.sample.address.last_modified_at
        self.assertIsNotNone(last_modified)

        self.sample.name = "Joe"
        self.assertTrue(self.sample.save(), self.sample.errors.full_messages)

        self.assertNotEqual(
            last_modified,
            self.sample.address.last_modified_at
        )

    def test_unique_field(self):
        self.sample.name = "John"
        assert self.sample.save(), self.sample.errors.full_messages

        another_sample = self.Sample(name="Mike")
        assert another_sample.save(), another_sample.errors.full_messages

        another_sample.name = "John"
        self.assertFalse(another_sample.save())

        self.assertEqual(
            ["Name must be unique"],
            another_sample.errors.full_messages
        )
