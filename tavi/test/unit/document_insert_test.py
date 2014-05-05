# -*- coding: utf-8 -*-
import pymongo
import unittest
from bson.objectid import ObjectId
from pymongo import MongoClient
from tavi.documents import EmbeddedDocument, Document
from tavi import fields


class Address(EmbeddedDocument):
    street = fields.StringField("street")
    created_at = fields.DateTimeField("created_at")
    last_modified_at = fields.DateTimeField("last_modified_at")


class DocumentInsertTest(unittest.TestCase):
    class Sample(Document):
        name = fields.StringField("name", required=True, unique=True)
        created_at = fields.DateTimeField("created_at")
        last_modified_at = fields.DateTimeField("last_modified_at")
        address = fields.EmbeddedField("address", Address)
        status = fields.StringField("my_status")

    def setUp(self):
        super(DocumentInsertTest, self).setUp()
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

    def test_uses_mongo_field_names(self):
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

    def test_does_not_add_created_at_if_not_present(self):
        class AnotherAddress(EmbeddedDocument):
            street = fields.StringField("street")

        class AnotherSample(Document):
            name = fields.StringField("name", required=True, unique=True)
            address = fields.EmbeddedField("address", AnotherAddress)

        address = AnotherAddress(street="42 Wood St.")
        sample = AnotherSample(name="John")
        sample.address = address

        assert sample.save(), sample.errors.full_messages
        self.assertFalse(hasattr(sample, "created_at"))
        self.assertFalse(hasattr(sample.address, "created_at"))

        record = list(self.db.another_samples.find())[0]
        self.assertNotIn("created_at", record)
        self.assertNotIn("created_at", record["address"])

    def test_sets_created_at_if_present(self):
        self.sample.name = "John"
        self.assertTrue(self.sample.save())
        self.assertIsNotNone(self.sample.created_at)

    def test_sets_created_at_for_any_embedded_documents(self):
        address = Address(street="123 Elm St.")
        self.sample.name = "John"
        self.sample.address = address
        self.assertTrue(self.sample.save())
        self.assertIsNotNone(self.sample.address.created_at)

    def test_does_not_set_created_at_if_invalid(self):
        self.assertIsNone(self.sample.created_at)
        self.sample.save()
        self.assertIsNone(self.sample.created_at)

    def test_does_not_set_created_at_if_error(self):
        self.sample.name = "John"
        self.assertIsNone(self.sample.created_at)
        with self.assertRaises(pymongo.errors.OperationFailure):
            self.sample.save(w=3)
        self.assertIsNone(self.sample.created_at)

    def test_does_not_set_embedded_doc_created_at_if_invalid(self):
        address = Address(street="123 Elm St.")
        self.sample.address = address

        self.assertIsNone(self.sample.address.created_at)
        self.sample.save()
        self.assertIsNone(self.sample.address.created_at)

    def test_does_not_set_embedded_doc_created_at_if_error(self):
        address = Address(street="123 Elm St.")
        self.sample.name = "John"
        self.sample.address = address
        self.assertIsNone(self.sample.address.created_at)

        with self.assertRaises(pymongo.errors.OperationFailure):
            self.sample.save(w=3)
        self.assertIsNone(self.sample.address.created_at)

    def test_does_not_save_if_invalid(self):
        self.sample.name = None
        self.sample.save()
        self.assertEqual(0, self.db.samples.count())

    def test_save_returns_false_if_failure(self):
        self.sample.name = None
        self.assertEqual(False, self.sample.save())

    def test_does_not_add_last_modified_if_not_present(self):
        class AnotherAddress(EmbeddedDocument):
            street = fields.StringField("street")

        class AnotherSample(Document):
            name = fields.StringField("name", required=True, unique=True)
            address = fields.EmbeddedField("address", AnotherAddress)

        address = AnotherAddress(street="42 Wood St.")
        sample = AnotherSample(name="John")
        sample.address = address

        assert sample.save(), sample.errors.full_messages
        self.assertFalse(hasattr(sample, "last_modified_at"))
        self.assertFalse(hasattr(sample.address, "last_modified_at"))

        record = list(self.db.another_samples.find())[0]
        self.assertNotIn("last_modified_at", record)
        self.assertNotIn("last_modified_at", record["address"])

    def test_does_not_set_last_modified_if_invalid(self):
        self.assertIsNone(self.sample.last_modified_at)
        self.assertFalse(self.sample.save())
        self.assertIsNone(self.sample.last_modified_at)

    def test_does_not_set_last_modified_if_error(self):
        self.sample.name = "John"
        self.assertIsNone(self.sample.last_modified_at)
        with self.assertRaises(pymongo.errors.OperationFailure):
            self.sample.save(w=3)
        self.assertIsNone(self.sample.last_modified_at)

    def test_does_not_set_embedded_doc_last_modified_if_invalid(self):
        address = Address(street="123 Elm St.")
        self.sample.address = address

        self.assertIsNone(self.sample.address.last_modified_at)
        self.sample.save()
        self.assertIsNone(self.sample.address.last_modified_at)

    def test_does_not_set_embedded_doc_last_modified_if_error(self):
        address = Address(street="123 Elm St.")
        self.sample.name = "John"
        self.sample.address = address
        self.assertIsNone(self.sample.address.last_modified_at)

        with self.assertRaises(pymongo.errors.OperationFailure):
            self.sample.save(w=3)
        self.assertIsNone(self.sample.address.last_modified_at)

    def test_change_list_is_cleared_after_saving(self):
        self.sample.name = "my sample"
        self.assertEqual(set(["name"]), self.sample.changed_fields)
        self.sample.save()
        self.assertEqual(set(), self.sample.changed_fields)

    def test_unique_field_on_insert(self):
        self.sample.name = "John"
        assert self.sample.save(), self.sample.errors.full_messages

        another_sample = self.Sample(name="John")
        self.assertIsNone(another_sample.created_at)
        self.assertFalse(another_sample.save())

        self.assertEqual(
            ["Name must be unique"],
            another_sample.errors.full_messages
        )
        self.assertIsNone(another_sample.created_at)
