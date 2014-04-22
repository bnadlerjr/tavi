# -*- coding: utf-8 -*-
import unittest
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from tavi.documents import EmbeddedDocument, Document
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


class EmbeddedDocumentTest(unittest.TestCase):
    class Sample(EmbeddedDocument):
        first_name = fields.StringField("first_name")
        last_name = fields.StringField("last_name")

    def test_equal_if_all_attributes_equal(self):
        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        self.assertTrue(sample_a == sample_b)
        self.assertTrue(sample_b == sample_a)

    def test_unequal_if_attributes_are_not_equal(self):
        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = self.Sample(
            first_name="James",
            last_name="Doe"
        )

        self.assertFalse(sample_a == sample_b)
        self.assertFalse(sample_b == sample_a)

    def test_unequal_if_not_exact_same_type(self):
        class AnotherSample(self.Sample):
            pass

        sample_a = self.Sample(
            first_name="John",
            last_name="Doe"
        )

        sample_b = AnotherSample(
            first_name="John",
            last_name="Doe"
        )

        self.assertFalse(sample_a == sample_b)
        self.assertFalse(sample_b == sample_a)

    def test_unequal_if_one_is_none(self):
        self.assertFalse(self.Sample is None)
