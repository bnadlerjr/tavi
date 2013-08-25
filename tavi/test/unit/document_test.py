import unittest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from tavi.connection import Connection
from tavi.errors import TaviConnectionError
from tavi.document import EmbeddedDocument, Document
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
            ), self.Sample.collection)

class DocumentSaveTest(unittest.TestCase):
    class Sample(Document):
        name = fields.StringField("name", required=True)

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

    def test_save_returns_true_if_success(self):
        self.sample.name = "John"
        self.assertTrue(self.sample.save())

    def test_assigns_object_id(self):
        self.sample.name = "John"
        self.sample.save()
        self.assertIsNotNone(self.sample.bson_id)

    def test_does_not_save_if_invalid(self):
        self.sample.name = None
        self.sample.save()
        self.assertEqual(0, self.db.samples.count())

    def test_save_returns_false_if_failure(self):
        self.sample.name = None
        self.assertEqual(False, self.sample.save())

    def test_save_updates_existing_documents(self):
        self.sample.name = "John"
        self.sample.save()

        self.sample.name = "Joe"
        self.sample.save()

        self.assertEqual(1, self.db.samples.count())
        actual = list(self.db.samples.find())[0]
        self.assertEqual("Joe", actual['name'])

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
        last_name  = fields.StringField("last_name",  required=True)

    def setUp(self):
        super(DocumentFindTest, self).setUp()
        client = MongoClient()
        client.drop_database("test_database")
        self.db = client['test_database']
        self.ids = self.db.samples.insert([
            { "first_name": "John", "last_name": "Doe" },
            { "first_name": "Joe",  "last_name": "Smith" },
            { "first_name": "John", "last_name": "Smith" }
        ])

        self.assertEqual(3, self.db.samples.count())

    def test_find_one(self):
        result = self.Sample.find_one(self.ids[0])
        self.assertEqual("John", result.first_name)

    def test_find_one_does_not_find_any(self):
        self.assertIsNone(self.Sample.find_one({"first_name": "No such name"}))

    def test_find_by_id_using_bson_id(self):
        result = self.Sample.find_by_id(self.ids[1])
        self.assertEqual("Joe", result.first_name)

    def test_find_by_id_using_string_id(self):
        result = self.Sample.find_by_id(str(self.ids[1]))
        self.assertEqual("Joe", result.first_name)

    def test_find(self):
        result = self.Sample.find({ "last_name": "Smith" })
        self.assertEqual(2, len(result))
        self.assertEqual("Smith", result[0].last_name)
        self.assertEqual("Smith", result[1].last_name)

    def test_find_all(self):
        result = self.Sample.find_all()
        self.assertEqual(3, len(result))

    def test_find_all_when_collection_is_empty(self):
        self.db.drop_collection("samples")
        self.assertEqual([], self.Sample.find_all())
