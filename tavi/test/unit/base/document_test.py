import unittest
from tavi.base.document import BaseDocument
from tavi.document import EmbeddedDocument
from tavi.fields import EmbeddedField, ListField, StringField

class BaseDocumentNoFieldsTest(unittest.TestCase):
    class NoFieldsSample(BaseDocument):
        pass

    def setUp(self):
        super(BaseDocumentNoFieldsTest, self).setUp()
        self.no_fields_sample = self.NoFieldsSample()

    def test_get_fields(self):
        self.assertEqual([], self.no_fields_sample.fields)

    def test_get_errors(self):
        self.assertEqual(0, self.no_fields_sample.errors.count)

    def test_valid(self):
        self.assertEqual(True, self.no_fields_sample.valid)

    def test_get_data(self):
        self.assertEqual({}, self.no_fields_sample.data)

# --------------------------------------------------------------------------- #

class Address(EmbeddedDocument):
    street = StringField("street")
    city = StringField("city")

class BaseDocumentFieldsTest(unittest.TestCase):
    class Sample(BaseDocument):
        name = StringField("name", required=True)
        password = StringField("password", persist=False)

    class SampleWithEmbeddedField(BaseDocument):
        name = StringField("name", required=True)
        address = EmbeddedField("address", Address)

    class SampleWithEmbeddedListField(BaseDocument):
        addresses = ListField("addresses")

    def setUp(self):
        super(BaseDocumentFieldsTest, self).setUp()
        self.sample = self.Sample()

    def test_get_fields(self):
        self.assertEqual(["name"], self.sample.fields)

    def test_get_errors(self):
        self.sample.name = None
        self.assertEqual(["Name is required"], self.sample.errors.full_messages)

    def test_valid_when_no_errors(self):
        self.sample.name = "test"
        self.assertTrue(self.sample.valid, "expected sample to be valid")

    def test_invalid_when_errors(self):
        self.sample.name = None
        self.assertFalse(self.sample.valid, "expected sample to be invalid")

    def test_init_with_kwargs(self):
        sample = self.Sample(name="John")
        self.assertEqual("John", sample.name)

    def test_init_ignore_non_field_kwargs(self):
        sample = self.Sample(name="John", not_a_field=True)
        self.assertEqual("John", sample.name)

    def xtest_init_with_kwargs_does_not_overwrite_attributes(self):
        class User(BaseDocument):
            first_name = StringField("first_name")
            last_name  = StringField("last_name")

        user_a = User(first_name="John", last_name="Doe")
        user_b = User(first_name="Walter", last_name="White")

        self.assertEqual("John", user_a.first_name)
        self.assertEqual("Doe", user_a.last_name)

        self.assertEqual("Walter", user_b.first_name)
        self.assertEqual("White", user_b.last_name)

    def test_init_multiple_does_not_overwrite_attributes(self):
        class User(BaseDocument):
            first_name = StringField("first_name")
            last_name  = StringField("last_name")

        user_a = User()
        user_a.first_name = "John"
        user_a.last_name  = "Doe"

        user_b = User()
        user_b.first_name = "Walter"
        user_b.last_name  = "White"

        self.assertEqual("John", user_a.first_name)
        self.assertEqual("Doe", user_a.last_name)

        self.assertEqual("Walter", user_b.first_name)
        self.assertEqual("White", user_b.last_name)

    def test_get_data(self):
        sample = self.Sample(name="John")
        self.assertEqual({ "name": "John" }, sample.data)

    def test_get_data_with_single_embedded_field(self):
        sample = self.SampleWithEmbeddedField(name="John")
        sample.address.street = "123 Elm St."
        sample.address.city = "Anywhere"

        self.assertEqual({
            "name": "John",
            "address": {
                "street": "123 Elm St.",
                "city": "Anywhere"
            } }, sample.data)

    def test_get_data_with_embedded_list_field(self):
        sample = self.SampleWithEmbeddedListField()
        address = Address(street="123 Elm Street", city="Anywhere")

        sample.addresses.append(address)

        self.assertEqual({
            "addresses": [{
                "street": "123 Elm Street",
                "city": "Anywhere"
            }]}, sample.data)
