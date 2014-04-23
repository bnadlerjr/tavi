# -*- coding: utf-8 -*-
import unittest
from bson.objectid import ObjectId
from pymongo import MongoClient
from tavi.documents import EmbeddedDocument, Document
from tavi import fields


class Address(EmbeddedDocument):
    street = fields.StringField("street")
    created_at = fields.DateTimeField("created_at")
    last_modified_at = fields.DateTimeField("last_modified_at")


class DocumentSaveTest(unittest.TestCase):
    class Sample(Document):
        name = fields.StringField("name", required=True)
        created_at = fields.DateTimeField("created_at")
        last_modified_at = fields.DateTimeField("last_modified_at")
        address = fields.EmbeddedField("address", Address)
        status = fields.StringField("my_status")

    def setUp(self):
        super(DocumentSaveTest, self).setUp()
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']
        self.sample = self.Sample()

    def test_saves_the_document(self):
        self.sample.name = "John"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("John", actual['name'])

    def test_upserts_document_if_id_is_given(self):
        self.sample._id = ObjectId()
        self.sample.name = "John"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("John", actual['name'])

    def test_save_uses_mongo_field_names_on_insert(self):
        self.sample.name = "John"
        self.sample.status = "inactive"
        self.sample.save()

        actual = list(self.db.samples.find())[0]
        self.assertEqual("inactive", actual['my_status'])

    def test_save_returns_true_if_success(self):
        self.sample.name = "John"
        self.assertTrue(self.sample.save())

    def test_assigns_object_id(self):
        self.sample.name = "John"
        self.sample.save()
        self.assertIsNotNone(self.sample.bson_id)

    def test_save_sets_created_at_if_present(self):
        self.sample.name = "John"
        self.assertTrue(self.sample.save())
        self.assertIsNotNone(self.sample.created_at)

    def test_save_sets_created_at_for_any_embedded_documents(self):
        address = Address(street="123 Elm St.")
        self.sample.name = "John"
        self.sample.address = address
        self.assertTrue(self.sample.save())
        self.assertIsNotNone(self.sample.address.created_at)

    def test_does_not_save_if_invalid(self):
        self.sample.name = None
        self.sample.save()
        self.assertEqual(0, self.db.samples.count())

    def test_save_returns_false_if_failure(self):
        self.sample.name = None
        self.assertEqual(False, self.sample.save())

    def test_save_uses_mongo_field_names_on_update(self):
        self.sample.name = "John"
        self.sample.status = "active"
        self.sample.save()

        self.sample.status = "inactive"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("inactive", actual['my_status'])

    def test_save_updates_existing_documents(self):
        self.sample.name = "John"
        self.sample.save()

        self.sample.name = "Joe"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("Joe", actual['name'])

    def test_save_sets_last_modified_if_present(self):
        self.sample.name = "John"
        self.sample.save()
        last_modified = self.sample.last_modified_at
        self.assertIsNotNone(last_modified)

        self.sample.name = "Joe"
        self.sample.save()
        self.assertNotEqual(last_modified, self.sample.last_modified_at)

    def test_save_sets_last_modified_for_any_embedded_documents(self):
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

    def test_change_list_is_cleared_after_saving(self):
        self.sample.name = "my sample"
        self.assertEqual(set(["name"]), self.sample.changed_fields)
        self.sample.save()
        self.assertEqual(set(), self.sample.changed_fields)
